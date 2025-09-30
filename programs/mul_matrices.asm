# Matriz 3x2 por 2x4 con números naturales
# Datos (A y B) desde 1028, resultado desde 20455, programa desde 3700

# --------------------
# Datos
# --------------------
ORG 1028

MAT_A:  # 3x2 (row-major)
DW 1, 2
DW 3, 4
DW 5, 6

MAT_B:  # 2x4 (row-major)
DW 7, 8, 9, 10
DW 11, 12, 13, 14


# --------------------
# Buffer de salida C (3x4)
# --------------------
ORG 20455
RES: RESW 12   # 3*4 = 12 palabras de 64 bits


# --------------------
# Código
# --------------------
ORG 3700

START:
	# Bases
	MOVI R1, MAT_A      # base A
	MOVI R2, MAT_B      # base B
	MOVI R3, RES        # base C (salida)

	# Dimensiones
	MOVI R4, 3          # p = filas(A) = 3
	MOVI R5, 2          # m = cols(A) = filas(B) = 2
	MOVI R6, 4          # n = cols(B) = 4
	MOVI R7, 8          # tamaño de palabra (bytes)

	# --------------------
	# Entrada: leer A (3 filas, 2 columnas) y B (2 filas, 4 columnas)
	# Cada fila se ingresa como linea con numeros separados por espacio
	# IN Rcount, Rbase, N   con func=subop(parse-line)+sep ' '
	# --------------------
	# Leer A
	# Prompt: "A rows (3x2):\n"
	MOVI R8, 65   # 'A'
	OUT  R8, 0xFFFF0000
	MOVI R8, 32   # ' '
	OUT  R8, 0xFFFF0000
	MOVI R8, 114  # 'r'
	OUT  R8, 0xFFFF0000
	MOVI R8, 111  # 'o'
	OUT  R8, 0xFFFF0000
	MOVI R8, 119  # 'w'
	OUT  R8, 0xFFFF0000
	MOVI R8, 115  # 's'
	OUT  R8, 0xFFFF0000
	MOVI R8, 32   # ' '
	OUT  R8, 0xFFFF0000
	MOVI R8, 40   # '('
	OUT  R8, 0xFFFF0000
	MOVI R8, 51   # '3'
	OUT  R8, 0xFFFF0000
	MOVI R8, 120  # 'x'
	OUT  R8, 0xFFFF0000
	MOVI R8, 50   # '2'
	OUT  R8, 0xFFFF0000
	MOVI R8, 41   # ')'
	OUT  R8, 0xFFFF0000
	MOVI R8, 58   # ':'
	OUT  R8, 0xFFFF0000
	MOVI R8, 10   # '\n'
	OUT  R8, 0xFFFF0000

	MOVI R10, 0          # i = 0
A_in_loop:
	CP  R12, R10         # offset filas: (i*2)*8
	ADD R12, R12, R12
	MUL R12, R12, R7
	ADD R14, R1, R12     # R14 = &A[i][0]
	IN  R15, R14, 2      # lee 2 numeros en A[i][0..1]
	ADDI R10, R10, 1
	CMP  R0, R10, R4
	JNZ  A_in_loop

	# Leer B
	# Prompt: "B rows (2x4):\n"
	MOVI R8, 66   # 'B'
	OUT  R8, 0xFFFF0000
	MOVI R8, 32   # ' '
	OUT  R8, 0xFFFF0000
	MOVI R8, 114  # 'r'
	OUT  R8, 0xFFFF0000
	MOVI R8, 111  # 'o'
	OUT  R8, 0xFFFF0000
	MOVI R8, 119  # 'w'
	OUT  R8, 0xFFFF0000
	MOVI R8, 115  # 's'
	OUT  R8, 0xFFFF0000
	MOVI R8, 32   # ' '
	OUT  R8, 0xFFFF0000
	MOVI R8, 40   # '('
	OUT  R8, 0xFFFF0000
	MOVI R8, 50   # '2'
	OUT  R8, 0xFFFF0000
	MOVI R8, 120  # 'x'
	OUT  R8, 0xFFFF0000
	MOVI R8, 52   # '4'
	OUT  R8, 0xFFFF0000
	MOVI R8, 41   # ')'
	OUT  R8, 0xFFFF0000
	MOVI R8, 58   # ':'
	OUT  R8, 0xFFFF0000
	MOVI R8, 10   # '\n'
	OUT  R8, 0xFFFF0000

	MOVI R10, 0          # i = 0..m-1
B_in_loop:
	CP  R12, R10         # offset filas: (i*4)*8
	ADD R12, R12, R12
	ADD R12, R12, R12
	MUL R12, R12, R7
	ADD R14, R2, R12     # &B[i][0]
	IN  R15, R14, 4      # lee 4 numeros en B[i][0..3]
	ADDI R10, R10, 1
	CMP  R0, R10, R5
	JNZ  B_in_loop

	# --------------------
	# Imprimir matriz A
	# --------------------
	MOVI R8, 65          # 'A'
	OUT  R8, 0xFFFF0000
	MOVI R8, 58          # ':'
	OUT  R8, 0xFFFF0000
	MOVI R8, 10          # '\n'
	OUT  R8, 0xFFFF0000

	MOVI R10, 0          # i = 0 (filas A)
A_i_print:
	# fila base &A[i][0]  => offset = (i*2)*8
	CP  R12, R10         # R12 = i
	ADD R12, R12, R12    # i*2
	MUL R12, R12, R7     # (i*2)*8
	ADD R14, R1, R12     # R14 = &A[i][0]
	# OUT fila de 2 enteros con separador ' ' (func = 514)
	OUT R14, 2, 514
	# fin de fila
	MOVI R8, 10          # '\n'
	OUT  R8, 0xFFFF0000

	ADDI R10, R10, 1
	CMP  R0, R10, R4     # i < p ?
	JNZ  A_i_print

	# --------------------
	# Imprimir matriz B
	# --------------------
	MOVI R8, 66          # 'B'
	OUT  R8, 0xFFFF0000
	MOVI R8, 58          # ':'
	OUT  R8, 0xFFFF0000
	MOVI R8, 10          # '\n'
	OUT  R8, 0xFFFF0000

	MOVI R10, 0          # i = 0 (filas B = m)
B_i_print:
	# fila base &B[i][0] => offset = (i*4)*8
	CP  R12, R10         # R12 = i
	ADD R12, R12, R12    # *2
	ADD R12, R12, R12    # *4
	MUL R12, R12, R7     # *8
	ADD R14, R2, R12     # R14 = &B[i][0]
	OUT R14, 4, 514
	# fin de fila
	MOVI R8, 10
	OUT  R8, 0xFFFF0000

	ADDI R10, R10, 1
	CMP  R0, R10, R5     # i < m ?
	JNZ  B_i_print

	# i = 0
	MOVI R10, 0

i_loop:
	# j = 0
	MOVI R11, 0

j_loop:
	# sum = 0
	MOVI R13, 0
	# k = 0
	MOVI R12, 0

k_loop:
	# --------------------
	# A[i][k]
	# idxA = (i*2) + k
	CP  R8, R10          # R8 = i
	ADD R8, R8, R8       # R8 = i*2
	ADD R8, R8, R12      # R8 = i*2 + k
	MUL R9, R8, R7       # R9 = (idxA)*8 (bytes)
	ADD R14, R1, R9      # R14 = &A[i][k]
	LD  R8, R14, 0       # R8 = A[i][k]

	# B[k][j]
	# idxB = (k*4) + j
	CP  R9, R12          # R9 = k
	ADD R9, R9, R9       # R9 = k*2
	ADD R9, R9, R9       # R9 = k*4
	ADD R9, R9, R11      # R9 = k*4 + j
	MUL R9, R9, R7       # R9 = (idxB)*8 (bytes)
	ADD R14, R2, R9      # R14 = &B[k][j]
	LD  R9, R14, 0       # R9 = B[k][j]

	# sum += A[i][k] * B[k][j]
	MUL R8, R8, R9       # R8 = A*B
	ADD R13, R13, R8     # sum += R8

	# k++ y comparar con m
	ADDI R12, R12, 1
	CMP  R0, R12, R5
	JNZ  k_loop

	# --------------------
	# C[i][j] = sum
	# idxC = (i*4) + j
	CP  R8, R10          # R8 = i
	ADD R8, R8, R8       # i*2
	ADD R8, R8, R8       # i*4
	ADD R8, R8, R11      # i*4 + j
	MUL R8, R8, R7       # (idxC)*8
	ADD R14, R3, R8      # &C[i][j]
	ST  R13, R14, 0      # C[i][j] = sum

	# j++ y comparar con n
	ADDI R11, R11, 1
	CMP  R0, R11, R6
	JNZ  j_loop

	# i++ y comparar con p
	ADDI R10, R10, 1
	CMP  R0, R10, R4
	JNZ  i_loop

	# --------------------
	# Imprimir matriz resultado C (3x4)
	# --------------------
	MOVI R8, 67          # 'C'
	OUT  R8, 0xFFFF0000
	MOVI R8, 58          # ':'
	OUT  R8, 0xFFFF0000
	MOVI R8, 10          # '\n'
	OUT  R8, 0xFFFF0000

	MOVI R10, 0          # i = 0 (filas C = p)
C_i_print:
	# fila base &C[i][0] => offset = (i*4)*8
	CP  R12, R10
	ADD R12, R12, R12    # *2
	ADD R12, R12, R12    # *4
	MUL R12, R12, R7     # *8
	ADD R14, R3, R12     # &C[i][0]
	OUT R14, 4, 514
	# fin de fila
	MOVI R8, 10
	OUT  R8, 0xFFFF0000

	ADDI R10, R10, 1
	CMP  R0, R10, R4     # i < p ?
	JNZ  C_i_print

	HALT


