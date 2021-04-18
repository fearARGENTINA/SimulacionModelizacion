#!/usr/bin/python3

import re
from abc import ABC, abstractmethod

ERROR_INVALID_LINE = "Linea de codigo invalida (Instruccion inexistente o sintaxis incorrecta)"
ERROR_INVALID_PARAMS = "Linea de codigo invalida (Problema en parametros! ¿Cantidad de parametros? ¿Registros invalidos? ¿Parametros no esperados? )"
ERROR_INVALID_JUMP = "Linea de codigo invalida (No existe etiqueta)"

class Instruccion(ABC):
    def __init__(self):
        self.params = []
    
    def setParams(self, params : list):
        self.params = params
    
    def getParams(self):
        return self.params
        
    @abstractmethod
    def validar(self):
        pass
    
    @abstractmethod
    def procesar(self, procesador):
        pass

class Mov(Instruccion):
    def validar(self, line):
        if re.search("^mov\s+(ax|bx|cx|dx)\s+(ax|bx|cx|dx|\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.setRegister(params[0], params[1])
        
class Add(Instruccion):
    def validar(self, line):
        if re.search("^add\s+(ax|bx|cx|dx)\s+(ax|bx|cx|dx|\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        if params[1].isnumeric():
            auxSecParam = params[1]
        else:
            auxSecParam = f"self.{params[1]}"
        
        procesador.setRegister(params[0], f"self.{params[0]}+{auxSecParam}")
            
class Jmp(Instruccion):
    def validar(self, line):
        if re.search("^jmp\s+\w+$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.setRegister("ip", params[0])
        
class Jnz(Instruccion):
    def validar(self, line):
        if re.search("^jnz\s+\w+$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        if procesador.getRegister("flag"):
            procesador.setRegister("ip", params[0])
        
class Cmp(Instruccion):
    def validar(self, line):
        if re.search("^cmp\s+(ax|bx|cx|dx|\d+)\s+(ax|bx|cx|dx|\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        val1 = params[0]
        val2 = params[1]
        
        if not params[0].isnumeric():
            val1 = procesador.getRegister(params[0])
        
        if not params[1].isnumeric():
            val2 = procesador.getRegister(params[1])
        
        procesador.setRegister("flag", f"int({val1}<={val2})")

class Inc(Instruccion):
    def validar(self, line):
        if re.search("^inc\s+(ax|bx|cx|dx)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.setRegister(params[0], "self.{params[0]}+1")
        
class Dec(Instruccion):
    def validar(self, line):
        if re.search("^dec\s+(ax|bx|cx|dx)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.setRegister(params[0], "self.{params[0]}-1")

VALID_INSTRUCTIONS = { "mov" : Mov, "add" : Add , "jmp" : Jmp, "jnz" : Jnz, "cmp" : Cmp, "inc" : Inc, "dec" : Dec}

class Ensamblador:
    def __init__(self):
        self.errors = []
        self.allJumps = []
        self.ejecutable = Ejecutable()
        
    def procesar(self, nombreArchivo):
        with open(nombreArchivo, "r") as file:
            self.ejecutable.setCodigoFuente( [ line.strip().replace('\n', '') for line in file.readlines() ] )
        
        listaInstLineNum = 0
        for fuenteLineNum, line in enumerate(self.ejecutable.getCodigoFuente()):
            if self.esEtiqueta(line):
                self.ejecutable.addLookupTable(self.subEtiqueta(line), listaInstLineNum)
            elif self.esInstruccion(line):
                preInstruccion = self.getInstruccion(line)
                instruccion = VALID_INSTRUCTIONS[preInstruccion]()
                
                try:
                    instruccion.validar(line)
                    params = line.split()[1:]
                    
                    if isinstance(instruccion, Jnz) or isinstance(instruccion, Jmp):
                        instruccion.setParams(params)
                        self.allJumps.append((fuenteLineNum, *instruccion.getParams(), listaInstLineNum))
                    else:
                        instruccion.setParams(params)
                        
                    self.ejecutable.addListaInstrucciones(instruccion)
                except Exception as e:
                    self.errors.append((fuenteLineNum, str(e)))
                
                listaInstLineNum += 1
            elif not len(line) or line[0] == "#":
                continue
            else:
                self.errors.append((fuenteLineNum, ERROR_INVALID_LINE))
        
        self.validarAllJumps()
        self.ejecutable.setEntryPoint()
        
    def esEtiqueta(self, line):
        return not re.search(r"^(\w+):$", line) is None
    
    def subEtiqueta(self, line):
        return re.findall(r"^(\w+):$", line)[0]
    
    def esInstruccion(self, line):
        return len(line) and line.split()[0] in VALID_INSTRUCTIONS.keys()
        
    def getInstruccion(self, line):
        return line.split()[0]
    
    def validarAllJumps(self):
        for fuenteLineNum, etiqueta, listaInstLineNum in self.allJumps:
            if self.ejecutable.getLookupTable(etiqueta) is None:
                self.errors.append((fuenteLineNum, ERROR_INVALID_JUMP))
            else:
                instruccion = self.ejecutable.getInstruccion(listaInstLineNum)
                toLabel = instruccion.getParams()[0]
                instruccion.setParams([self.ejecutable.getLookupTable(toLabel)])
        
    def getEjecutable(self):
        return self.ejecutable
    
    def getErrores(self):
        return self.errors
        
class Ejecutable:
    def __init__(self):
        self.codigoFuente = []
        self.lookupTable = dict()
        self.listaInstrucciones = []
        self.entryPoint = 0
    
    def setCodigoFuente(self, codigoFuente : str):
        self.codigoFuente = codigoFuente
    
    def getCodigoFuente(self):
        return self.codigoFuente

    def getListaInstrucciones(self):
        return self.listaInstrucciones
    
    def addListaInstrucciones(self, instruccion : Instruccion):
        self.listaInstrucciones.append(instruccion)
    
    def getInstruccion(self, num):
        return self.listaInstrucciones[num]
    
    def addLookupTable(self, key : str, value: int):
        self.lookupTable[key] = value
    
    def getLookupTable(self, key : str):
        return self.lookupTable.get(key)
    
    def setEntryPoint(self):
        self.entryPoint = self.lookupTable.get("entry_point", 0)
        
class Procesador:
    def __init__(self):
        self.ax = 0
        self.bx = 0
        self.cx = 0
        self.dx = 0
        self.ip = 0
        self.flag = 0
    
    def setRegister(self, register : str, value : str):
        exec(f"self.{register}={value}")
    
    def getRegister(self, register : str):
        return eval(f"self.{register}")
        
def main():
    ensamblador = Ensamblador()
    ensamblador.procesar("main.asm")
    print("------------------------ Errores ------------------------\n\n")
    for e in ensamblador.getErrores():
        print(e)
    print("------------------------ Lista Instr ------------------------\n\n")
    for i in ensamblador.getEjecutable().getListaInstrucciones():
        print(i)
    print("------------------------ Lookup Table ------------------------\n\n")
    print(ensamblador.getEjecutable().lookupTable)
    print("------------------------ allJumps ------------------------\n\n")
    print(ensamblador.allJumps)
    
main()