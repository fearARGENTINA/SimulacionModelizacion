# Este es un programa de ejemplo de cómo debería incorporarse la visualización del sistema de Teoría de Colas desarrollado en la primera parte del TP
# Modificar y completar todo lo que consideren necesario

import time
import curses
from curses import wrapper
from teoriaDeColas import *

def imprimirTitulo(screen):
	screen.addstr(0,0,'Servidores (O = ocupado, D = desocupado)')
	
def imprimirDatos(screen):
	servidores = 100
	fila = 1
	columna = 1
	for i in range(servidores):
		screen.addstr(fila,columna,'{:02d}: |   | '.format(i))
		if fila % 20 == 0:
			fila = 1
			columna += 20
		else:
			fila += 1

def actualizarEstadoServidores(screen, sistema):
	#servidores = 100
	fila = 1
	columna = 7
	listaOcupados = [servidor.estaOcupado for servidor in sistema.servidores]
    
	for ocupado in listaOcupados:
		if ocupado:
			screen.addstr(fila,columna,'O')
		else: 
			screen.addstr(fila,columna,'D')
		if fila % 20 == 0:
			fila = 1
			columna += 20
		else:
			fila += 1
	screen.refresh()
	#time.sleep(0.01)
    
	screen.addstr(22,0,'Cantidad de clientes en espera (en la cola): {}     '.format(sistema.cola.cantClientes()))
	screen.addstr(23,0,'Cantidad de mediciones: {}'.format(estadistica.cantMediciones))
	screen.addstr(24,0,'Tiempo global: {}'.format(sistema.tiempoGlobal))
	screen.addstr(26,0,'L: {}'.format(estadistica.L()))
	screen.addstr(27,0,'Lq: {}'.format(estadistica.Lq()))
	screen.addstr(26,50,'W: {}'.format(estadistica.W()))
	screen.addstr(27,50,'Wq: {}'.format(estadistica.Wq()))
    
	if (screen.getch() == ord('f')):
		return True
        
	return False
            
def iniciar(screen):
	#1) inicialización de variables	
	#2.1) crear instancia de estadistica
	#2.2) crear instancia de sistema	
	#3) llegada 1er. cliente
    
    # se le pasa lambda y mu
	CANT_SERVIDORES = 5
	TASAS_ATENCION = [4]*CANT_SERVIDORES
    
	cSistema = Sistema(2, TASAS_ATENCION)
    
	imprimirTitulo(screen)	
    
	imprimirDatos(screen)
	
	screen.nodelay(True)
	screen.refresh()
	cSistema.procesar(actualizarEstadoServidores, screen)
		

wrapper(iniciar)
