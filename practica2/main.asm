sumar:
	pop bx
	pop cx
	pop dx
	push bx
	add cx dx
	mov ax cx
	ret
	
# Multiplicar
multiplicar:
	pop bx
	pop cx
	pop dx
	push bx
	mov ax 0
loop:
	dec dx
	add ax cx
	cmp 1 dx
	jnz loop
	# set flag 0
	cmp 0 1
	ret

# Division entera (cx = dividendo, bx = divisor) => cx / bx **** Devuelve dx = cociente, cx = resto
dividir:
	pop ax
	pop bx
	pop cx
	push ax
	push bx
	# Multiplico por -1 uno de los valores para realizar la resta por suma, al finalizar el registro ax tendra el valor de bx (divisor) pero negativo
	mov ax 0
loop2:
	dec bx
	add ax -1
	cmp 1 bx
	jnz loop2
	pop bx
	mov dx 0
divoper:
	add cx ax
	cmp bx cx
	add dx 1
	jnz divoper
	ret

entry_point:
	push 8
	push 2
	call dividir
	cmp ax 1