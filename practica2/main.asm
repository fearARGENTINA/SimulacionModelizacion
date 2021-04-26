Sumar:
	pop bx
	pop cx
	pop dx
	push bx
	add cx dx
	mov ax cx
	ret

Etiqueta1:
	mov ax 50
	mov bx 3
	mov ax bx
	dec bx
	jmp Lol

entry_point:
	push 3
	push 5
	call Sumar
	cmp ax 1
Lol:
	cmp bx ax
	jnz entry_point
	# pepito comentario
