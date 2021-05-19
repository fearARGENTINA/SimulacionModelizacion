#!/usr/bin/python3

from abc import ABC, abstractmethod
import re
import curses
from time import sleep

ERROR_INVALID_LINE = "Linea de codigo invalida (Instruccion inexistente o sintaxis incorrecta)"
ERROR_INVALID_PARAMS = "Linea de codigo invalida (Problema en parametros! ¿Cantidad de parametros? ¿Registros invalidos? ¿Parametros no esperados? )"
ERROR_INVALID_JUMP = "Linea de codigo invalida (No existe etiqueta)"
ERROR_INVALID_INCLUDE = "Inclusion de codigo invalida (No existe el archivo)"
ERROR_REPEATED_LABEL = "Etiqueta definida mas de una vez"

PROCESO_ACTIVO      = 0
PROCESO_BLOQUEADO   = 1
PROCESO_FINALIZADO  = 2

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
        if re.search("^mov\s+(ax|bx|cx|dx)\s+(ax|bx|cx|dx|-?\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        if self.params[1].lstrip("-").isnumeric():
            auxSecParam = self.params[1]
        else:
            auxSecParam = f"self.{self.params[1]}"
        procesador.setRegister(self.params[0], auxSecParam)
        
        super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("mov")
    
class Add(Instruccion):
    def validar(self, line):
        if re.search("^add\s+(ax|bx|cx|dx)\s+(ax|bx|cx|dx|-?\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        if self.params[1].lstrip("-").isnumeric():
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
        if re.search("^cmp\s+(ax|bx|cx|dx|-?\d+)\s+(ax|bx|cx|dx|-?\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        val1 = self.params[0]
        val2 = self.params[1]
        
        if not self.params[0].lstrip("-").isnumeric():
            val1 = procesador.getRegister(self.params[0])
        
        if not self.params[1].lstrip("-").isnumeric():
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
        
class Push(Instruccion):
    def validar(self, line):
        if re.search("^push\s+(ax|bx|cx|dx|-?\d+)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.pushStack(self.params[0])
        
        super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("push")
        
class Pop(Instruccion):
    def validar(self, line):
        if re.search("^pop\s+(ax|bx|cx|dx)$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.popStack(self.params[0])
        
        super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("pop")

class Ret(Instruccion):
    def validar(self, line):
        if re.search("^ret$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
        
    def procesar(self, procesador):
        procesador.setRegister("ip", procesador.stack.pop())
        
        super().procesar(procesador)
    
    def mostrar(self):
        return super().mostrar("ret")

class Call(Instruccion):
    def __init__(self, retPointer : str):
        self.retPointer = retPointer
        super().__init__()
        
    def validar(self, line):
        if re.search("^call\s+\w+$", line) is None:
            raise Exception(ERROR_INVALID_PARAMS)
    
    def procesar(self, procesador):
        procesador.pushStack(self.retPointer)
        procesador.setRegister("ip", self.params[0])
    
    def mostrar(self):
        return super().mostrar("call")
        
VALID_INSTRUCTIONS = { 
    "mov" : Mov, 
    "add" : Add , 
    "jmp" : Jmp, 
    "jnz" : Jnz, 
    "cmp" : Cmp, 
    "inc" : Inc, 
    "dec" : Dec, 
    "call" : Call, 
    "pop" : Pop, 
    "push" : Push, 
    "ret" : Ret 
}

class Ensamblador:
    def __init__(self):
        self.errors = []
        self.allJumps = []
        self.ejecutable = None
        self.listaInstLineNum = 0
        
    def chequearIncludes(self, nombreArchivo):
        with open(nombreArchivo, "r") as file:
            lines = [ line.strip().replace('\n', '') for line in file.readlines() ]
            allIncludes = list(filter(lambda x: self.esInclude(x[1]), enumerate(lines)))

            for fuenteLineNum, line in allIncludes:
                file = line.split()[1]
                try:
                    f = open(file)
                    self.chequearIncludes(file)
                    f.close()
                except Exception as e:
                    if not len(self.errors):
                        self.errors.append((fuenteLineNum, nombreArchivo, ERROR_INVALID_INCLUDE))
                    
                    raise Exception(e)                    
        
    def procesarEjecutable(self, nombreArchivo):
        self.ejecutable = Ejecutable()
        
        with open(nombreArchivo, "r") as file:
            codigoFuente = [ line.strip().replace('\n', '') for line in file.readlines() ]
        
        for fuenteLineNum, line in enumerate(codigoFuente):
            if self.esEtiqueta(line):
                nombreEtiqueta = self.subEtiqueta(line)
                if self.ejecutable.getLookupTable(nombreEtiqueta):
                    self.errors.append((fuenteLineNum, nombreArchivo, ERROR_REPEATED_LABEL))
                else:
                    self.ejecutable.addLookupTable(nombreEtiqueta, self.listaInstLineNum)
            elif self.esInclude(line):
                includeArchivo = line.split()[1]
                
                self.procesarEjecutable(includeArchivo)
            elif self.esInstruccion(line):
                preInstruccion = self.getInstruccion(line)
                if preInstruccion == "call":
                    instruccion = VALID_INSTRUCTIONS[preInstruccion](str(self.listaInstLineNum))
                else:
                    instruccion = VALID_INSTRUCTIONS[preInstruccion]()
                
                try:
                    params = line.split()[1:]
                    
                    instruccion.setParams(params)
                    
                    if isinstance(instruccion, Jnz) or isinstance(instruccion, Jmp) or isinstance(instruccion, Call):
                        self.allJumps.append((fuenteLineNum, nombreArchivo, *instruccion.getParams(), self.listaInstLineNum))
                        
                    self.ejecutable.addListaInstrucciones(instruccion)
                    instruccion.validar(line)
                except Exception as e:
                    self.errors.append((fuenteLineNum, nombreArchivo, str(e)))
                
                self.listaInstLineNum += 1
            elif not len(line) or line[0] == "#":
                continue
            else:
                self.errors.append((fuenteLineNum, nombreArchivo, ERROR_INVALID_LINE))
    
    def procesar(self, nombreArchivo):
        try:
            self.chequearIncludes(nombreArchivo)
        except Exception as e:
            return
        
        self.procesarEjecutable(nombreArchivo)
                
        self.validarAllJumps()
        self.ejecutable.setEntryPoint()
    
    def limpiar(self):
        self.errors = []
        self.allJumps = []
        self.ejecutable = None
        self.listaInstLineNum = 0
    
    def esInclude(self, line):
        return not re.search(r"^include[\s]+[\w.]+$", line) is None
    
    def esEtiqueta(self, line):
        return not re.search(r"^(\w+):$", line) is None
    
    def subEtiqueta(self, line):
        return re.findall(r"^(\w+):$", line)[0]
    
    def esInstruccion(self, line):
        return len(line) and line.split()[0] in VALID_INSTRUCTIONS.keys()
        
    def getInstruccion(self, line):
        return line.split()[0]
    
    def validarAllJumps(self):
        for fuenteLineNum, nombreArchivo, etiqueta, listaInstLineNum in self.allJumps:
            if self.ejecutable.getLookupTable(etiqueta) is None:
                self.errors.append((fuenteLineNum, nombreArchivo, ERROR_INVALID_JUMP))
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

class Visualizador:
    def __init__(self, anchoCodigo, anchoProcesador, altoPantalla, filaInstruccion):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        self.anchoCodigo = anchoCodigo
        self.anchoProcesador = anchoProcesador
        self.alto = altoPantalla
        self.filaInstruccion = filaInstruccion
        
    def mostrar(self, ejecutable, procesador, procesoActivo):
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
        
        self.dibujar(dataShow, procesador.mostrar(), procesoActivo)
        
        self.stdscr.refresh()
                
    def dibujar(self, lineasCodigo, dataProcesador, procesoActivo):
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
        
        self.stdscr.addstr(self.alto+1, 0, f"PROCESO EN EJECUCION: {procesoActivo}")
        
    def pressedQuit(self):
        return self.stdscr.getch() == ord('q')

class Procesador:
    def __init__(self):
        self.procesoActivo = None
        self.ax = 0
        self.bx = 0
        self.cx = 0
        self.dx = 0
        self.ip = 0
        self.flag = 0
        self.stack = []
    
    def setRegister(self, register : str, value : str):
        exec(f"self.{register}={value}")
    
    def getRegister(self, register : str):
        return eval(f"self.{register}")
    
    def setProcesoActivo(self, proceso):
        self.procesoActivo = proceso
    
    def pushStack(self, value : str):
        if not value.lstrip("-").isnumeric():
            self.stack.append(self.getRegister(value))
        else:
            self.stack.append(int(value))
    
    def popStack(self, register : str):
        exec(f"self.{register}=self.stack.pop()")
        
    def mostrar(self):
        return [
            ('ax', str(self.ax)),
            ('bx', str(self.bx)),
            ('cx', str(self.cx)),
            ('dx', str(self.dx)),
            ('ip', str(self.ip)),
            ('flag', str(self.flag)),
        ] + [ ('stack', str(value)) for value in self.stack ]
    
    def procesar(self, sistema):
        visualizador = sistema.visualizador
        ejecutable = self.procesoActivo.getEjecutable()
        listaInstrucciones = ejecutable.getListaInstrucciones()
        
        while self.ip < len(listaInstrucciones):
            '''
            if self.procesoActivo.getEstado() == PROCESO_BLOQUEADO or self.procesoActivo.getEstado() == PROCESO_FINALIZADO:
                print(f"EL PROCESO ACTIVO ELEGIDO ESTA MAL: {self.procesoActivo.getEstado()}")
                break
            '''
            
            print(listaInstrucciones[self.ip])
            visualizador.mostrar(self.procesoActivo.getEjecutable(), self, sistema.procesoActivo)
            listaInstrucciones[self.ip].procesar(self)
            sistema.clockHandler()
            #sleep(0.01)
            
            if visualizador.pressedQuit():
                break
            
            ejecutable = self.procesoActivo.getEjecutable()
            listaInstrucciones = ejecutable.getListaInstrucciones()
                
    def getContexto(self):
        return {
            'ax': self.ax,
            'bx': self.bx,
            'cx': self.cx,
            'dx': self.dx,
            'ip': self.ip,
            'flag': self.flag,
            'stack' : self.stack
        }
        
    def setContexto(self, contexto):
        for key, value in contexto.items():
            exec(f"self.{key}={value}")
           
class ProcesosFinalizadosException(Exception):
    pass

class Proceso:
    def __init__(self, ejecutable, estado = PROCESO_BLOQUEADO):
        self.ejecutable = ejecutable
        self.contexto = {'ip' : ejecutable.getEntryPoint(), 'stack': [], 'ax': 0, 'bx': 0, 'cx': 0, 'dx': 0, 'flag': 0}
        self.estado = estado
        self.contadorInstrucciones = 0
        
    def cambiarEstado(self, estado, procesador):
        self.estado = estado
        self.contexto = procesador.getContexto()
        
    def getEstado(self):
        return self.estado
    
    def setEstado(self, estado):
        self.estado = estado
        
    def getEjecutable(self):
        return self.ejecutable
        
    def getContexto(self):
        return self.contexto
    
    def setContadorInstrucciones(self, contador):
        self.contadorInstrucciones = contador

class Sistema:
    def __init__(self, procesador : Procesador, procesos = []):
        self.procesador = procesador
        self.visualizador = Visualizador(14, 10, 15, 4)
        self.listaProcesos = procesos
        self.procesoActivo = None
        self.RAFAGA_INSTRUCCIONES = 5
        
    def pushProceso(self, procesos : list):
        self.listaProcesos += procesos
    
    def buscarSiguienteProceso(self):
        desdeProceso = self.procesoActivo
        
        while True:
            self.procesoActivo += 1
            
            if self.procesoActivo >= len(self.listaProcesos):
                self.procesoActivo = 0
            
            if self.listaProcesos[self.procesoActivo].getEstado() == PROCESO_BLOQUEADO:
                print(f"SE ENCONTRO PROCESO: {self.listaProcesos[self.procesoActivo]}")
                self.listaProcesos[self.procesoActivo].setEstado(PROCESO_ACTIVO)
                self.listaProcesos[self.procesoActivo].setContadorInstrucciones(0)
                self.procesador.setProcesoActivo(self.listaProcesos[self.procesoActivo])
                self.procesador.setContexto(self.listaProcesos[self.procesoActivo].getContexto())
                break
                
            if self.procesoActivo == desdeProceso:
                raise ProcesosFinalizadosException("Se finalizaron todos los procesos en la lista de procesos")

    def clockHandler(self):        
        self.listaProcesos[self.procesoActivo].contadorInstrucciones += 1
        ejecutable = self.listaProcesos[self.procesoActivo].getEjecutable()
        
        if self.procesador.getRegister("ip") >= len(ejecutable.getListaInstrucciones()):
            self.listaProcesos[self.procesoActivo].cambiarEstado(PROCESO_FINALIZADO, self.procesador)
            
            self.buscarSiguienteProceso()
        elif self.listaProcesos[self.procesoActivo].contadorInstrucciones >= self.RAFAGA_INSTRUCCIONES:
            print("SE ALCANZO RAFAGA DE INSTRUCCIONES")
            self.listaProcesos[self.procesoActivo].cambiarEstado(PROCESO_BLOQUEADO, self.procesador)
            
            self.buscarSiguienteProceso()
                     
    
    def procesar(self):
        if len(self.listaProcesos):
            self.procesoActivo = 0
            self.procesador.setProcesoActivo(self.listaProcesos[0])
            self.procesador.setContexto(self.listaProcesos[0].getContexto())
            self.procesador.procesar(self)
        else:
            print("No existen procesos en la lista de procesos...")
        
def main():
    procesador = Procesador()
    ensamblador = Ensamblador()
    
    codigosFuentes = [("proceso1.asm", PROCESO_ACTIVO)]
    procesos = []
    hayError = False
    
    for i, codigo in enumerate(codigosFuentes):
        ensamblador.procesar(codigo[0])
        if len(ensamblador.getErrores()):
            for error in ensamblador.getErrores():
                print(error)
            
            hayError = True
            ensamblador.limpiar()
            break
            
        procesos += [Proceso(ensamblador.getEjecutable(), codigo[1])]
        
        print(f"PROCESO {procesos[i]}")
        print(f"CONTEXTO DE PROCESO {i}")
        print(procesos[i].getContexto())
        print(f"\n\nLISTA INSTRUCCIONES PROCESO {i}")
        for a in ensamblador.getEjecutable().getListaInstrucciones():
            print(a)
            
        print("\n\n#######################################################\n\n")
        
        ensamblador.limpiar()
    
    if not hayError:
        sistema = Sistema(procesador, procesos)
        
        try:
            sistema.procesar()
        except ProcesosFinalizadosException as e:
            print(e)
            print("Finalizaron todos los procesos o no existen procesos por ejecutar...")
            sleep(5)
            
    
main()