sumar:
	pop bx
	pop cx
	pop dx
	push bx
	add cx dx
	mov ax cx
	ret

# Division entera (cx = dividendo, bx = divisor) => cx / bx **** Devuelve dx = cociente, cx = resto
dividir:
	pop ax
	pop bx
	pop cx
	push ax
	# Multiplico por -1 uno de los valores para realizar la resta por suma, al finalizar el registro ax tendra el valor de bx (divisor) pero negativo
	push cx
	push bx
	push bx
	push -1
	call multiplicar
	pop bx
	pop cx
loop_div:
	add cx ax
	cmp bx cx
	inc dx
	jnz loop_div
	cmp 1 0
	ret
	
# Multiplicacion entera (bx = factor, cx = factor) => bx * cx **** Devuelve ax = producto
multiplicar:
	pop bx
	pop cx
	pop dx
	push bx
	mov ax 0
loop_mult:
	dec dx
	add ax cx
	cmp 1 dx
	jnz loop_mult
	cmp 1 0
	ret
	
#	************* Metodo de Newton *************
#	def isqrt(n):
#		x = n
#		y = (x + 1) // 2
#		while y < x:
#			x = y
#			y = (x + n // x) // 2
#		return x
# Si x es cx ==> raiz(n) = x ==> raiz(n) = cx
raiz:
	pop ax
	# bx = radicando (parametro n)
	pop bx
	push ax
	# x = n (cx = bx)
	mov cx bx
	# y = (x + 1) // 2
	mov dx cx
	inc dx
	push bx
	push cx
	push dx
	push 2
	call dividir
	pop cx
	pop bx
	# Recordatorio (bx = radicando, cx = x, dx = y)
	# while y < x:
	cmp cx dx
	jnz fin_raiz
loop_raiz:
	# x = y
	mov cx dx
	# dx = n // x
	push bx
	push cx
	push bx
	push cx
	call dividir
	pop cx
	pop bx
	# dx = y = x + n // x = x + dx
	push bx
	push cx
	push cx
	push dx
	call sumar
	mov dx ax
	pop cx
	pop bx
	# dx = dx // 2
	push bx
	push cx
	push dx
	push 2
	call dividir
	pop cx
	pop bx
	# x = y
	# y = (x + n // x) // 2
	# ax = ?
	# bx = n = radicando
	# cx = x
	# dx = y
	# y < x = y <= x - 1
	mov ax cx
	dec ax
	cmp dx ax
	jnz loop_raiz
fin_raiz:
	cmp 1 0
	ret
	
# def fib(n):
#     if n < 2:
#         return n
#     else:
#         # fn = fn-1 + fn-2
#         return fib(n-1) + fib(n-2)
# Fibonacci devuelve en bx
fibonacci:
	pop ax
	pop bx
	push ax
	cmp 2 bx
	jnz calcular_fibonacci
	ret
calcular_fibonacci:
	mov cx bx
	dec cx
	push cx
	push cx
	call fibonacci
	# cx = n - 1
	pop cx
	# ax = fib(n-1)
	# cx = n - 2
	dec cx
	push bx
	push cx
	call fibonacci
	# bx = fib(n-2)
	pop ax
	push ax
	push bx
	call sumar
	mov bx ax
	ret


# A*x^2 + B*X + C
# (-B +- sqrt(B^2-4*A*C))/(2*A)
raiz_cuadratica:
	pop dx
	# A = ax, B = bx, C = cx
	pop cx
	pop bx
	pop ax
	push dx
	push ax
	push bx
	push cx
	push ax
	push 2
	call multiplicar
	mov dx ax
	pop cx
	pop bx
	pop ax
	# Meto en stack 2*A
	push dx
	push ax
	push bx
	push cx
	push bx
	push -1
	call multiplicar
	mov dx ax
	pop cx
	pop bx
	pop ax
	# Meto en stack -B
	push dx
	push ax
	push bx
	push cx
	push bx
	push bx
	call multiplicar
	mov dx ax
	pop cx
	pop bx
	pop ax
	# Meto en stack B^2
	push dx
	push ax
	push bx
	push cx
	push ax
	push cx
	call multiplicar
	mov dx ax
	pop cx
	pop bx
	pop ax
	# dx = A * C
	push ax
	push bx
	push cx
	push dx
	push -4
	call multiplicar
	mov dx ax
	pop cx
	pop bx
	pop ax
	# Meto en stack -4*A*C
	push dx
	call sumar
	# ax = B^2-4*A*C
	push ax
	call raiz
	# cx = sqrt(B^2-4*A*C)
	# Meto en stack sqrt(B^2-4*A*C)
	push cx
	# En este punto el stack es el siguiente:
	# 2*A
	# -B
	# sqrt(B^2-4*A*C)
	push cx
	push -1
	call multiplicar
	push ax
	# En este punto el stack es el siguiente:
	# 2*A 				= ax
	# -B				= bx
	# sqrt(B^2-4*A*C)	= cx
	# -sqrt(B^2-4*A*C)	= dx
	pop dx
	pop cx
	pop bx
	pop ax
	push ax
	push bx
	push cx
	push ax
	# -B - sqrt(B^2-4*A*C)
	push bx
	push dx
	call sumar
	push ax
	call dividir
	# dx = (-B - sqrt(B^2-4*A*C))/(2*A)
	pop cx
	pop bx
	pop ax
	# Meto en stack dx = (-B - sqrt(B^2-4*A*C))/(2*A)
	push dx
	push ax
	push bx
	push cx
	call sumar
	push ax
	call dividir
	# dx =  (-B + sqrt(B^2-4*A*C))/(2*A)
	pop cx
	ret
	