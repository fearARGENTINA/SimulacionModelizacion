include funciones.asm

# (x-4)(x-2) = x^2 -6x +8
# (x+4)(x-2) = x^2 + 2x -8
# (x+4)(x+2) = x^2 + 6x + 8

entry_point:
	push 1
	push 6
	push 8
	call raiz_cuadratica
	cmp 6 0
	
