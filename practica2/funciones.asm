# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
# ****************************************			SUMA ENTERA								**********************************************************
# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
sumar:
	pop bx
	pop cx
	pop dx
	push bx
	add cx dx
	mov ax cx
	ret

# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
# ****************************************			NEGATIVO ENTERO							**********************************************************
# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
negativo:
	pop ax
	pop bx
	push ax
	mov flag bx
	jnz negativo_bx_isnotzero
	mov ax 0
	ret
negativo_bx_isnotzero:
	mov ax 0
	cmp 0 bx
	jnz negativo_bx_ispos
negativo_bx_isneg:
	inc bx
	inc ax
	cmp bx -1
	jnz negativo_bx_isneg
	ret
negativo_bx_ispos:
	dec bx
	dec ax
	cmp 1 bx
	jnz negativo_bx_ispos
	ret


# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
# ****************************************			DIVISION ENTERA							**********************************************************
# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
# Division entera (cx = dividendo, bx = divisor) => cx / bx **** Devuelve dx = cociente, cx = resto
dividir:
	pop ax
	pop bx
	pop cx
	push ax
	mov ax 0
	mov dx 0
	mov flag cx
	jnz dividir_dividendo_notzero
	mov cx 0
	mov dx 0
	ret
dividir_dividendo_notzero:
	push cx
	push bx
	push bx
	cmp 0 cx
	jnz dividir_cx_ispos
	push cx
	call negativo
	mov cx ax
dividir_cx_ispos:
	pop bx
	push cx
	cmp 0 bx
	jnz dividir_bx_ispos
	push bx
	call negativo
	mov bx ax
dividir_bx_ispos:
	pop cx
	# Multiplico por -1 uno de los valores para realizar la resta por suma, al finalizar el registro ax tendra el valor de bx (divisor) pero negativo
	cmp bx cx
	jnz dividir_normal_flow
	pop bx
	pop cx
	mov dx 0
	ret
dividir_normal_flow:
	push cx
	push bx
	push bx
	call negativo
	pop bx
	pop cx
dividir_loop:
	add cx ax
	cmp bx cx
	inc dx
	jnz dividir_loop
	pop bx
	pop ax
	push cx
	push ax
	push dx
	push ax
	push bx
	call multiplicar2
	cmp 0 ax
	jnz dividir_check_sign_resto
	call negativo
	push ax
dividir_check_sign_resto:
	pop dx
	pop ax
	push dx
	cmp 0 ax
	jnz dividir_finish
	pop dx
	pop cx
	push dx
	push cx
	call negativo
	pop dx
	push ax
	push dx
dividir_finish:
	pop dx
	pop cx
	ret

# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
# ****************************************			MULTIPLICACION ENTERA					**********************************************************
# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
#def mult(bx, cx):
#    if bx == 0 or cx == 0:
#        return 0
#    else:
#        if bx < 0:
#			if cx > 0:
#           	return bx + mult(bx, cx - 1)
#        	elif cx < 0:
#            return -cx + mult(-bx - 1, -cx)
#        else:
#            return cx + mult(bx - 1, cx)
multiplicar:
	pop ax
	pop bx
	pop cx
	push ax
	# if bx == 0
	mov flag bx
	jnz check_cx
	jmp some_zero
check_cx:
	# or if cx == 0
	mov flag cx
	jnz ret_notzeros
	# return 0
some_zero:
	mov ax 0
	ret
	# else: (bx != 0 y cx != 0)
ret_notzeros:
	# if bx < 0:
	cmp bx -1
	jnz bx_isneg
	# else: (bx > 0)
	# return cx + multiplicar2(bx-1, cx)
	push cx
	dec bx
	push bx
	push cx
	call multiplicar2
	push ax
	call sumar
	ret
bx_isneg:
	# cx > 0 -> cx:
	cmp 0 cx
	jnz cx_ispos
	# cx < 0:
	push bx
	push cx
	call negativo
	# cx = -cx_antiguo
	mov cx ax
	call negativo
	# bx = -bx_antiguo
	mov bx ax
	push cx
	dec bx
	push bx
	push cx
	call multiplicar2
	push ax
	call sumar
	ret
	# cx > 0:
cx_ispos:
	push bx
	dec cx
	push bx
	push cx
	call multiplicar2
	push ax
	call sumar
	ret


# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
# ****************************************			RAIZ CUADRADA ENTERA					**********************************************************
# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
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

# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
# ****************************************			FIBONACCI								**********************************************************
# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
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

# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
# ****************************************			RAIZ CUADRATICA							**********************************************************
# ****************************************************************************************************************************************************
# ****************************************************************************************************************************************************
# A*x^2 + B*X + C
# (-B +- sqrt(B^2-4*A*C))/(2*A)
# CX = RAIZ 1 (POSITIVA), DX = RAIZ 2 (NEGATIVA)
raiz_cuadratica:
	pop dx
	pop cx
	pop bx
	pop ax
	push dx
	push cx
	push bx
	push ax
	push ax
	push 2
	call multiplicar2
	mov dx ax
	pop ax
	pop bx
	pop cx
	# PUSHEO AL STACK DX QUE ES IGUAL A 2*A = 2*ax
	push dx
	push cx
	push bx
	push ax
	push bx
	call negativo
	mov dx ax
	pop ax
	pop bx
	pop cx
	# PUSHEO AL STACK DX QUE ES IGUAL A -B = -bx
	push dx
	push cx
	push bx
	push ax
	push bx
	push bx
	call multiplicar2
	mov dx ax
	pop ax
	pop bx
	pop cx
	# PUSHEO AL STACK DX QUE ES IGUAL A B^2 = bx^2
	push dx
	push ax
	push cx
	call multiplicar2
	push ax
	push -4
	call multiplicar2
	mov dx ax
	# PUSHEO AL STACK DX QUE ES IGUAL A -4*A*C = -4*ax*cx
	push dx
	call sumar
	push ax
	call raiz
	push cx
	push cx
	call negativo
	# 2*A = dx
	# -B = cx
	# SQRT(B^2-4*A*C) = bx
	# -SQRT(B^2-4*A*C) = ax
	pop bx
	pop cx
	pop dx
	push dx
	push cx
	push bx
	push dx
	push cx
	push ax
	call sumar
	pop dx
	push ax
	push dx
	call dividir
	# EN AX TENEMOS (-B - sqrt(B^2-4*A*C))/(2*A)
	mov ax dx
	pop bx
	pop cx
	pop dx
	push ax
	push dx
	push cx
	push bx
	call sumar
	pop dx
	push ax
	push dx
	call dividir
	pop cx
	ret