#!/usr/bin/python3

from abc import ABC, abstractmethod
import re
import curses
from time import sleep

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

    def procesar(self, procesador):
        procesador.setRegister("ip", procesador.getRegister("ip")+1)
    
    def mostrar(self, prefix):
        return f"{prefix} {' '.join(map(lambda x: str(x), self.getParams()))}"
        
    @abstractmethod
    def validar(self):
        pass
    
class Mov(Instruccion):
    def validar(self, line):
        if re.search("^mov\s+(ax|bx|cx|dx)\s+(ax|bx|cx|dx|\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        if self.params[1].isnumeric():
            auxSecParam = self.params[1]
        else:
            auxSecParam = f"self.{self.params[1]}"
        procesador.setRegister(self.params[0], auxSecParam)
        
        super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("mov")
    
class Add(Instruccion):
    def validar(self, line):
        if re.search("^add\s+(ax|bx|cx|dx)\s+(ax|bx|cx|dx|\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        if self.params[1].isnumeric():
            auxSecParam = self.params[1]
        else:
            auxSecParam = f"self.{self.params[1]}"
        
        procesador.setRegister(self.params[0], f"self.{self.params[0]}+{auxSecParam}")
        
        super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("add")
        
class Jmp(Instruccion):
    def validar(self, line):
        if re.search("^jmp\s+\w+$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.setRegister("ip", self.params[0])
    
    def mostrar(self):
        return super().mostrar("jmp")
        
class Jnz(Instruccion):
    def validar(self, line):
        if re.search("^jnz\s+\w+$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        if procesador.getRegister("flag"):
            procesador.setRegister("ip", self.params[0])
        else:
            super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("jnz")
        
class Cmp(Instruccion):
    def validar(self, line):
        if re.search("^cmp\s+(ax|bx|cx|dx|\d+)\s+(ax|bx|cx|dx|\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        val1 = self.params[0]
        val2 = self.params[1]
        
        if not self.params[0].isnumeric():
            val1 = procesador.getRegister(self.params[0])
        
        if not self.params[1].isnumeric():
            val2 = procesador.getRegister(self.params[1])
        
        procesador.setRegister("flag", f"int({val1}<={val2})")
        
        super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("cmp")
        
class Inc(Instruccion):
    def validar(self, line):
        if re.search("^inc\s+(ax|bx|cx|dx)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.setRegister(self.params[0], f"self.{self.params[0]}+1")
        
        super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("inc")
        
class Dec(Instruccion):
    def validar(self, line):
        if re.search("^dec\s+(ax|bx|cx|dx)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.setRegister(self.params[0], f"self.{self.params[0]}-1")
        
        super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("dec")
    
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
    
    def getEntryPoint(self):
        return self.entryPoint
        
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
        
    def mostrar(self):
        return [
            ('ax', str(self.ax)),
            ('bx', str(self.bx)),
            ('cx', str(self.cx)),
            ('dx', str(self.dx)),
            ('ip', str(self.ip)),
            ('flag', str(self.flag))
        ]

class Visualizador:
    def __init__(self, anchoCodigo, anchoProcesador, altoPantalla, filaInstruccion):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        self.anchoCodigo = anchoCodigo
        self.anchoProcesador = anchoProcesador
        self.alto = altoPantalla
        self.filaInstruccion = filaInstruccion
        
    def mostrar(self, ejecutable, procesador):
        allInstrucciones = ejecutable.getListaInstrucciones()
        self.instructionPointer = procesador.getRegister("ip")
        
        minShow = self.instructionPointer - self.filaInstruccion
        maxShow = self.instructionPointer + (self.alto - self.filaInstruccion)
        
        instrucciones = allInstrucciones[max(0, minShow):maxShow]
        
        firstPadding = max(self.filaInstruccion - self.instructionPointer, 0)
        dataShow = [""]*firstPadding + list(map(lambda instruccion: instruccion.mostrar(), instrucciones))
        
        if len(dataShow) > self.alto:
            dataShow = dataShow[:self.alto]
        elif len(dataShow) < self.alto:
            dataShow += [""]*(self.alto-len(dataShow))
        
        self.stdscr.clear()
        
        self.dibujar(dataShow, procesador.mostrar())
        
        self.stdscr.refresh()
        
                
    def dibujar(self, lineasCodigo, dataProcesador):
        for fila in range(0, self.alto):
            if fila == self.filaInstruccion:
                self.stdscr.addstr(fila, 0, ">")
            else:
                self.stdscr.addstr(fila, 0, " ")
            
            for col in range(0, min(self.anchoCodigo, len(lineasCodigo[fila]))):
                self.stdscr.addstr(fila, 1+col, lineasCodigo[fila][col])
                
            self.stdscr.addstr(fila, self.anchoCodigo, "|")
            
            if fila < len(dataProcesador):
                line = " : ".join(dataProcesador[fila])
                
                for col in range(0, min(self.anchoProcesador, len(line))):
                    self.stdscr.addstr(fila, self.anchoCodigo+1+col, line[col])
        
    def pressedQuit(self):
        return self.stdscr.getch() == ord('q')
        
class Sistema:
    def __init__(self, ejecutable : Ejecutable, procesador : Procesador):
        self.ejecutable = ejecutable
        self.procesador = procesador
        self.visualizador = Visualizador(15, 9, 9, 4)
        
    def procesar(self):
        self.procesador.setRegister("ip", self.ejecutable.getEntryPoint())
        
        listaInstrucciones = self.ejecutable.getListaInstrucciones()
        
        self.visualizador.mostrar(self.ejecutable, self.procesador)
        sleep(2)
        while self.procesador.getRegister("ip") < len(listaInstrucciones):
            self.visualizador.mostrar(self.ejecutable, self.procesador)
            instructionPointer = self.procesador.getRegister("ip")
            listaInstrucciones[instructionPointer].procesar(self.procesador)
            sleep(2)
            
            if self.visualizador.pressedQuit():
                break
        
def main():
    ensamblador = Ensamblador()
    ensamblador.procesar("main.asm")
    procesador = Procesador()
    
    if not len(ensamblador.getErrores()):
        sistema = Sistema(ensamblador.getEjecutable(), procesador)
        sistema.procesar()
    
main()