import heapq
import numpy as np

#comentarios:
# A continuacion se detalla el esqueleto de la primera parte del trabajo de Teoria de Colas. 
# El modelo que seguiremos es el de un supermercado con una cola y multiples servidores (o cajas de atencion) 
# prefijo de las variables:
#	f: float
#	i: int
#	v*: vector o lista de tipo *
#   c: instancia de una clase

CANTIDAD_SERVIDORES = 5

def distribucionExponencial(lamda):
  return np.random.exponential(scale=1/lamda)

class Cliente:
	def __init__(self, fTiempoLlegada):
	# inicializa las variables y setea el tiempo de llegada del cliente
        self.tiempoLlegada = fTiempoLlegada

	def setTiempoInicioAtencion(self,fTiempoInicioAtencion):
	# setter del tiempo del inicio de atencion del cliente
        self.tiempoInicioAtencion = fTiempoInicioAtencion
	
	def setTiempoSalida(self, fTiempoSalida):
	# setter del tiempo de salida del cliente
        self.tiempoFinDeAtencion = fTiempoSalida
		
class Sistema:
	def __init__(self, fTasaLlegadaClientes, fTasasAtencionServidores):
	# inicializa: la tasa de llegada de clientes, el tiempo global
        self.Lambda = fTasaLlegadaClientes
        self.mu = fTasaAtencionServidor
	# crea la cola de clientes
        self.cola = Cola()
	# crea la lista de servidores (llama al metodo creacionServidores)
        self.servidores = self.creacionServidores()
	# crea la bolsa de eventos
        self.crearBolsaEventos()

    def crearBolsaEventos(self):
        self.eventos = []
        heapq.heapify(self.eventos)

    def agregarEvento(self, evento):
        heapq.heappush(self.eventos, evento)

    def proximoEvento(self):
        return heapq.heappop(self.eventos)

	def creacionServidores(self):
	# crea la lista de servidores respetando la respectivas tasa de atención
        return [ Servidor(self.mu) ] * CANTIDAD_SERVIDORES
	
	def eventoProximoCliente(self):
	# genera un evento de tipo EventoProximoCliente
	
	def ingresoCliente(self): 
	# callback para la clase EventoProximoCliente.procesar
	# corresponde a la llegada efectiva del cliente
	# 1) crea el Cliente
        cliente = Cliente(1/self.Lambda)
	# 2) agrega el cliente a la cola
        self.cola.llegaCliente(cliente)
	# 3) crea el nuevo evento de llegada del proximo cliente (llama a self.eventoProximoCliente())
        eventoProximoCliente = self.eventoProximoCliente()
		
	def procesar(self):
	# es el metodo más importante porque orquesta toda la simulacion 
	# 1) crea el eventoProximoCliente del 1er. cliente
        evento = self.eventoProximoCliente()
	# while (True):
        while (True):
	#	2) saca el proximo evento de la bolsa de eventos
            proximoEvento = self.proximoEvento()
    #	3) procesa el evento (via polimorfismo)
            proximoEvento.procesar()
	#	4) for s in self.servidores:
            for s in self.servidores:
			# 5) si el servidor esta desocupado y hay algun cliente en la cola
                if not s.estaOcupado and self.cola.cantClientes():
				# 6) desencolar el primer cliente de la cola
                    proximoCliente = self.cola.proximoCliente()
                    if proximoCliente is not None:
				# 7) generar el evento de FinAtencion 
                        eventoFinAtencion = EventoFinAtencion(proximoCliente.tiempoInicioAtencion, s)
				# 8) agregar a la bolsa de eventos el evento de FinAtencion
                        self.agregarEvento(eventoFinAtencion)
	
class Servidor:
	def __init__(self,fTasaAtencionServidor):
	# inicializa variables
        self.mu = fTasaAtencionServidor
        self.estaOcupado = False
		
	def estaOcupado(self):
	# flag: devuelve "true" si el servidor esta ocupado, y "false" si no
        return self.estaOcupado
		
	def inicioAtencion(self, fTiempoGlobal,cCliente):
	# setea el servidor en "ocupado"
        self.estaOcupado = True
	# setea el tiempo de inicio atencion del cliente
        self.cliente = cCliente
        cCliente.setTiempoInicioAtencion(fTiempoGlobal) 
	# crea y devuelve el EventoFinAtencion
        eventoFinAtencion = eventoFinAtencion(fTiempoGlobal + (1/self.mu), self)
        return eventoFinAtencion

	def finAtencion(self,fTiempo):
	# callback para EventoFinAtencion.procesar
	# setea el tiempo de salida del cliente
        self.cliente.setTiempoSalida(fTiempo)
        self.cliente = None
	# setea la servidor es desocupado
        self.estaOcupado = False

class Cola:
	def __init__(self):
	# crea la lista que representara la cola de clientes
	self.cola = []

	def cantClientes(self):
	# devuelve la cantidad de clientes que hay en la cola
        return len(self.cola)

	def llegaCliente(self,cCliente):
	# agregar el cliente a la cola
        self.cola.append(cCliente)
		
	def proximoCliente(self):
	# devuelve el primer cliente de la cola (si hay alguno)
        if self.cantClientes() != 0:
            return self.cola.pop()
        return None


# clase base de los eventos 	
class Evento:
	def __init__(self, fTiempo):
	# setea el tiempo de ocurrencia futura del evento
        self.tiempo = fTiempo
		
	# metodo "lower than" para comparar 2 eventos
	def __lt__(self, other):
		return self.tiempo < other.tiempo
	
	# metodo "gerater than" para comparar 2 eventos
	def __gt__(self, other):
		return self.tiempo > other.tiempo

	# metodo abstracto (debe ser implementado por las subclases)
	def procesar(self):
		pass

#evento correspondiente a la futura finalizacion de atencion de un cliente por parte de un servidor
class EventoFinAtencion(Evento):

	def __init__(self, fTiempo, cServidor):
	#llama al constructor de la superclase
        super(fTiempo)
	#setea el servidor
        self.servidor = cServidor

	def procesar(self):
	# llama a servidor.finAtencion
        self.servidor.finAtencion(self.tiempo)

#evento correspondiente a la futura llegada del proximo cliente
class EventoProximoCliente(Evento):
	
	def __init__(self, cSistema, fTiempo):
	#llama al constructor de la susperclase
        super(fTiempo)
	#setea el sistema (notar que recibe el sistema como parametro)
        self.sistema = cSistema
	
	def procesar(self):
	# llama al callback sistema.ingresoCliente()
        self.sistema.ingresoCliente()

# se le pasa lambda y mu
sistema = Sistema(...,...)
sistema.procesar()
