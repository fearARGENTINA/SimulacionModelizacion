import heapq
import numpy as np
from estadistica import Estadistica

estadistica = Estadistica()

#comentarios:
# A continuacion se detalla el esqueleto de la primera parte del trabajo de Teoria de Colas. 
# El modelo que seguiremos es el de un supermercado con una cola y multiples servidores (o cajas de atencion) 
# prefijo de las variables:
#	f: float
#	i: int
#	v*: vector o lista de tipo *
#   c: instancia de una clase

def distribucionExponencial(tasa):
	return (-1/tasa) * np.log(1-np.random.random())

class Cliente:
	def __init__(self, fTiempoLlegada):
		self.tiempoLlegada = fTiempoLlegada

	def setTiempoInicioAtencion(self,fTiempoInicioAtencion):
		self.tiempoInicioAtencion = fTiempoInicioAtencion
	
	def setTiempoSalida(self, fTiempoSalida):
		self.tiempoFinDeAtencion = fTiempoSalida
		
class Sistema:
	def __init__(self, fTasaLlegadaClientes, vfTasasAtencionServidores):
		self.vfTasasAtencionServidores = vfTasasAtencionServidores
		self.servidores = self.creacionServidores()
		self.Lambda = fTasaLlegadaClientes
		self.cola = Cola()
		self.eventos = []
		self.crearBolsaEventos()
		self.tiempoGlobal = 0

	def crearBolsaEventos(self):
		heapq.heapify(self.eventos)

	def agregarEvento(self, evento):
		heapq.heappush(self.eventos, evento)

	def proximoEvento(self):
		return heapq.heappop(self.eventos)

	def creacionServidores(self):
		return [Servidor(mu) for mu in self.vfTasasAtencionServidores]
		
	def eventoProximoCliente(self):
		evento = EventoProximoCliente(self, self.tiempoGlobal + distribucionExponencial(self.Lambda))
		self.agregarEvento(evento)
	
	def ingresoCliente(self): 
		cliente = Cliente(self.tiempoGlobal)
		self.cola.llegaCliente(cliente)
		self.eventoProximoCliente()
		
	def procesar(self, callbackActualizar, screen):
		#Primer Cliente
		self.eventoProximoCliente()
		while (True):
			estadistica.cantMediciones += 1
			proximoEvento = self.proximoEvento()
			self.tiempoGlobal = proximoEvento.tiempo
			proximoEvento.procesar()
			for servidor in self.servidores:
				if not servidor.estaOcupado and self.cola.cantClientes():
					proximoCliente = self.cola.proximoCliente()
					if proximoCliente != None:
						eventoFinAtencion = servidor.inicioAtencion(self.tiempoGlobal, proximoCliente)
						self.agregarEvento(eventoFinAtencion)
						estadistica.tiempoTotalClientesEnCola += proximoCliente.tiempoInicioAtencion - proximoCliente.tiempoLlegada
						estadistica.cantClientesQueEsperaron += 1
			print('Cant de cliente en cola', self.cola.cantClientes())
			
			estadosServidores = [servidor.estaOcupado for servidor in self.servidores]
			callbackActualizar(screen, estadosServidores)
			if self.cola.cantClientes() >= 10:
				print('FIN, Se llego al tope de clientes')
				return 
            

class Servidor:
	def __init__(self,fTasaAtencionServidor):
		self.mu = fTasaAtencionServidor
		self.estaOcupado = False
		
	def estaOcupado(self):
		return self.estaOcupado
		
	def inicioAtencion(self, fTiempoGlobal,cCliente):
		self.estaOcupado = True
		self.cliente = cCliente
		cCliente.setTiempoInicioAtencion(fTiempoGlobal) 
		eventoFinAtencion = EventoFinAtencion(fTiempoGlobal + distribucionExponencial(self.mu), self) 
		return eventoFinAtencion

	def finAtencion(self,fTiempo):
		self.cliente.setTiempoSalida(fTiempo)
		estadistica.tiempoTotalClientesEnSistema += self.cliente.tiempoFinDeAtencion - self.cliente.tiempoLlegada
		estadistica.cantClientesAtendidos += 1
		self.cliente = None
		self.estaOcupado = False

class Cola:
	def __init__(self):
		self.cola = []

	def cantClientes(self):
		return len(self.cola)

	def llegaCliente(self,cCliente):
		self.cola.append(cCliente)
		
	def proximoCliente(self):
		if self.cantClientes() != 0:
			return self.cola.pop()
		return None

# clase base de los eventos 	
class Evento:
	def __init__(self, fTiempo):
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
		super().__init__(fTiempo)
		self.servidor = cServidor

	def procesar(self):
		print('Fin Cliente')
		self.servidor.finAtencion(self.tiempo)

#evento correspondiente a la futura llegada del proximo cliente
class EventoProximoCliente(Evento):
	def __init__(self, cSistema, fTiempo):
		super().__init__(fTiempo)
		self.sistema = cSistema

	def procesar(self):
		print('Llego cliente')
		self.sistema.ingresoCliente()