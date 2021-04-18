Etiqueta1:
	mov ax 2	
	mov bx 3
	mov ax bx
	dec bx
	jmp Etiqueta2

entry_point:
	add bx ax
	jnz Etiqueta4
	# pepito comentario
Etiqueta2:
	cmp 1 3
	mov ax 1
	jmp Etiqueta3