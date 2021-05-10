include pepe.asm

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