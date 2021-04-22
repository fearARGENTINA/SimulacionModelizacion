Etiqueta1:
	mov ax 20000000000000000000000000
	mov bx 3
	mov ax bx
	dec bx
	jmp Lol

entry_point:
	mov bx 3
	add ax bx
	mov ax bx
	dec bx
	jmp Etiqueta1

Lol:
	cmp bx ax
	jnz entry_point
	# pepito comentario
