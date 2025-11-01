# ==================================================
# Demostracion de aritmetica de punto flotante
# Operaciones: suma, resta, multiplicacion y division
# ==================================================

# --------------------
# Seccion de datos
# --------------------
ORG 1024

num1:       DW 0x4025000000000000  # 10.5 en IEEE 754
num2:       DW 0x4034333333333333  # 20.2 en IEEE 754

ORG 2048
sum_result: RESW 1                 # Resultado de suma
sub_result: RESW 1                 # Resultado de resta
mul_result: RESW 1                 # Resultado de multiplicacion
div_result: RESW 1                 # Resultado de division

# --------------------
# Seccion de codigo
# --------------------
ORG 3700

START:
    # Imprimir encabezado
    MOVI R5, msg_header
    OUTS R5, 0xFFFF0008
    
    # Cargar operandos desde memoria
    MOVI R10, num1            # Direccion base de num1
    LD   R1, R10, 0           # R1 = num1 (10.5)
    MOVI R10, num2            # Direccion base de num2
    LD   R2, R10, 0           # R2 = num2 (20.3)
    
    # === SUMA FLOTANTE ===
    MOVI R5, msg_suma
    OUTS R5, 0xFFFF0008
    
    FADD R3, R1, R2           # R3 = 10.5 + 20.3 = 30.8
    MOVI R10, sum_result
    ST   R3, R10, 0           # Guardar resultado
    OUT  R3, 0xFFFF0008       # Imprimir resultado
    
    MOVI R6, 10               # Cargar newline
    OUT  R6, 0xFFFF0000
    
    # === RESTA FLOTANTE ===
    MOVI R5, msg_resta
    OUTS R5, 0xFFFF0008
    
    FSUB R4, R2, R1           # R4 = 20.3 - 10.5 = 9.8
    MOVI R10, sub_result
    ST   R4, R10, 0           # Guardar resultado
    OUT  R4, 0xFFFF0008       # Imprimir resultado
    
    MOVI R6, 10
    OUT  R6, 0xFFFF0000
    
    # === MULTIPLICACIoN ===
    MOVI R5, msg_mul
    OUTS R5, 0xFFFF0008
    
    FMUL R5, R1, R2           # R5 = 10.5 * 20.3 = 213.15
    MOVI R10, mul_result
    ST   R5, R10, 0           # Guardar resultado
    OUT  R5, 0xFFFF0008       # Imprimir resultado
    
    MOVI R6, 10
    OUT  R6, 0xFFFF0000
    
    # === DIVISIoN ===
    MOVI R5, msg_div
    OUTS R5, 0xFFFF0008
    
    FDIV R6, R2, R1           # R6 = 20.3 / 10.5 ≈ 1.933
    MOVI R10, div_result
    ST   R6, R10, 0           # Guardar resultado
    OUT  R6, 0xFFFF0008       # Imprimir resultado
    
    MOVI R6, 10
    OUT  R6, 0xFFFF0000
    
    # Imprimir mensaje de finalizacion
    MOVI R5, msg_fin
    OUTS R5, 0xFFFF0008
    
    HALT

# --------------------
# Strings (mensajes)
# --------------------
ORG 7680
msg_header: DB "=== Operaciones con Punto Flotante ===\n", 0
msg_suma:   DB "Suma (10.5 + 20.3) = ", 0
msg_resta:  DB "Resta (20.3 - 10.5) = ", 0
msg_mul:    DB "Multiplicacion (10.5 * 20.3) = ", 0
msg_div:    DB "Division (20.3 / 10.5) = ", 0
msg_fin:    DB "\nOperaciones completadas.\n", 0