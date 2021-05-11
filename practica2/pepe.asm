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

raiz:
	pop ax
	# bx = radicando (parametro n)
	pop bx
	push ax
	# x = n
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
	jmp fin_raiz
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
	
entry_point2:
	push 9
	call raiz
	cmp 6 0
	cmp 5 0
	cmp 4 0
	cmp 3 0
	cmp 2 0
	cmp 1 0
	