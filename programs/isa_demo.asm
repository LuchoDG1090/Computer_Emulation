# ===============================================================================
# DEMOSTRACIÓN COMPLETA DEL ISA - ARQUITECTURA DE 64 BITS
# ===============================================================================
#
# Este programa documenta y demuestra todas las instrucciones implementadas
# en el conjunto de instrucciones (ISA) de la arquitectura.
#
# FORMATO DE INSTRUCCIÓN (64 bits):
#   [63-56]: Opcode (8 bits)
#   [55-52]: RD - Registro destino (4 bits)
#   [51-48]: RS1 - Registro fuente 1 (4 bits)
#   [47-44]: RS2 - Registro fuente 2 (4 bits)
#   [43-32]: FUNC - Campo de función/modificadores (12 bits)
#   [31-0]:  IMM32 - Inmediato/dirección (32 bits)
#
# REGISTROS:
#   R0-R15: 16 registros de propósito general de 64 bits
#   R0: Típicamente usado como destino dummy en comparaciones
#
# FLAGS (8 bits en registro de estado):
#   Bit 0: ZERO (Z) - Resultado es cero
#   Bit 1: CARRY (C) - Acarreo en operaciones aritméticas
#   Bit 2: NEGATIVE (N) - Resultado negativo (bit de signo)
#   Bit 3: POSITIVE (P) - Resultado positivo
#   Bit 4: OVERFLOW (V) - Desbordamiento aritmético
#   Bit 5: INTERRUPT (I) - Habilitación de interrupciones
#
# DIRECCIONES MMIO (Memory-Mapped I/O):
#   0xFFFF0000: Salida de carácter (1 byte)
#   0xFFFF0008: Salida de entero/string
#   0xFFFF0010: Entrada de carácter (1 byte)
#   0xFFFF0018: Entrada de entero
#
# ===============================================================================

ORG 0x0

# ===============================================================================
# 1. INSTRUCCIONES DE TRANSFERENCIA DE DATOS (I-Type)
# ===============================================================================

# -----------------------------------------------------------------------------
# MOVI - Move Immediate (Mover inmediato a registro)
# -----------------------------------------------------------------------------
# Sintaxis: MOVI Rd, #imm32
# Codificación: Opcode=0x22, FUNC determina el tipo de dato
#   FUNC=0: Entero con signo (sign-extend 32→64 bits)
#   FUNC=2: Flotante (float32 en IMM32, convertido a double64 en registro)
# Flags: No afecta
# Uso: Cargar constantes enteras o flotantes en registros
# -----------------------------------------------------------------------------

MOVI R1, 42                 # R1 = 42 (entero positivo)
MOVI R2, -5                 # R2 = -5 (entero negativo, sign-extended)
MOVI R3, 0x2A               # R3 = 42 (hexadecimal)
MOVI R4, 0                  # R4 = 0

# MOVI con flotantes: el ensamblador detecta el punto decimal y codifica como float32
# El CPU convierte automáticamente a double precision (64 bits IEEE-754)
MOVI R5, 3.5                # R5 = 3.5 (double precision)
MOVI R6, 2.0                # R6 = 2.0 (double precision)
MOVI R7, -1.5               # R7 = -1.5 (double precision)

# -----------------------------------------------------------------------------
# CP - Copy Register (Copiar registro a registro)
# -----------------------------------------------------------------------------
# Sintaxis: CP Rd, Rs1
# Codificación: Opcode=0x29, FUNC=1
# Flags: No afecta
# Uso: Copiar el contenido de un registro a otro sin modificar flags
# -----------------------------------------------------------------------------

CP R8, R1                   # R8 = R1 (copia 42)

# -----------------------------------------------------------------------------
# OUT - Output (Salida a puerto/MMIO)
# -----------------------------------------------------------------------------
# Sintaxis: OUT Rs, port[, FUNC]
# Codificación: Opcode=0x61, IMM32=puerto/dirección, FUNC=modificadores
# FUNC bits [3:1] = subop:
#   0: Normal (entero con signo o carácter)
#   1: Array de enteros con signo (Rs=base, IMM32=count)
#   2: Entero con signo sin newline
#   3: Flotante (double precision)
#   4: Entero sin signo sin newline
#   5: Array de enteros sin signo (Rs=base, IMM32=count)
# FUNC bits [11:4] = separador ASCII (para arrays)
# Flags: No afecta
# Uso: Imprimir valores, arrays o strings a consola
# -----------------------------------------------------------------------------

# OUT básico: entero con signo
OUT R1, 0xFFFF0008          # Imprime 42 (entero con signo)
MOVI R10, 10
OUT R10, 0xFFFF0000         # Imprime newline (carácter ASCII 10)

# OUT con flotante: FUNC=6 es (3<<1)=subop 3
FDIV R9, R5, R6             # R9 = 3.5 / 2.0 = 1.75 (double)
OUT R9, 0xFFFF0008, 6       # Imprime 1.75 como flotante
OUT R10, 0xFFFF0000         # Newline

# ===============================================================================
# 2. INSTRUCCIONES ARITMÉTICAS Y LÓGICAS - ALU (R-Type)
# ===============================================================================

# -----------------------------------------------------------------------------
# ADD - Add (Suma de enteros con signo)
# -----------------------------------------------------------------------------
# Sintaxis: ADD Rd, Rs1, Rs2
# Codificación: Opcode=0x10
# Flags: Z, N, P, C (si hay acarreo), V (si hay overflow)
# Uso: Rd = Rs1 + Rs2 (aritmética de 64 bits con signo)
# -----------------------------------------------------------------------------

ADD R11, R1, R8             # R11 = 42 + 42 = 84

# -----------------------------------------------------------------------------
# SUB - Subtract (Resta de enteros con signo)
# -----------------------------------------------------------------------------
# Sintaxis: SUB Rd, Rs1, Rs2
# Codificación: Opcode=0x11
# Flags: Z, N, P, C, V
# Uso: Rd = Rs1 - Rs2
# -----------------------------------------------------------------------------

SUB R12, R11, R2            # R12 = 84 - (-5) = 89

# -----------------------------------------------------------------------------
# MUL - Multiply (Multiplicación de enteros con signo)
# -----------------------------------------------------------------------------
# Sintaxis: MUL Rd, Rs1, Rs2
# Codificación: Opcode=0x12
# Flags: Z, N, P, V (si resultado excede 64 bits)
# Uso: Rd = Rs1 * Rs2 (resultado truncado a 64 bits)
# -----------------------------------------------------------------------------

MUL R13, R1, R8             # R13 = 42 * 42 = 1764

# -----------------------------------------------------------------------------
# DIV - Divide (División entera con signo)
# -----------------------------------------------------------------------------
# Sintaxis: DIV Rd, Rs1, Rs2
# Codificación: Opcode=0x13
# Flags: Z, N, P
# Uso: Rd = Rs1 / Rs2 (división entera, redondeo hacia cero)
# Error: Genera excepción si Rs2 = 0
# -----------------------------------------------------------------------------

DIV R14, R13, R1            # R14 = 1764 / 42 = 42

# -----------------------------------------------------------------------------
# AND - Bitwise AND (AND lógico bit a bit)
# -----------------------------------------------------------------------------
# Sintaxis: AND Rd, Rs1, Rs2
# Codificación: Opcode=0x14
# Flags: Z, N, P
# Uso: Rd = Rs1 & Rs2
# -----------------------------------------------------------------------------

AND R15, R1, R2             # R15 = 42 & (-5)

# -----------------------------------------------------------------------------
# OR - Bitwise OR (OR lógico bit a bit)
# -----------------------------------------------------------------------------
# Sintaxis: OR Rd, Rs1, Rs2
# Codificación: Opcode=0x15
# Flags: Z, N, P
# Uso: Rd = Rs1 | Rs2
# -----------------------------------------------------------------------------

OR R1, R1, R2               # R1 = 42 | (-5)

# -----------------------------------------------------------------------------
# XOR - Bitwise XOR (XOR lógico bit a bit)
# -----------------------------------------------------------------------------
# Sintaxis: XOR Rd, Rs1, Rs2
# Codificación: Opcode=0x16
# Flags: Z, N, P
# Uso: Rd = Rs1 ^ Rs2
# -----------------------------------------------------------------------------

XOR R2, R8, R4              # R2 = 42 ^ 0 = 42

# -----------------------------------------------------------------------------
# NOT - Bitwise NOT (Complemento bit a bit)
# -----------------------------------------------------------------------------
# Sintaxis: NOT Rd, Rs1, Rs2
# Codificación: Opcode=0x17
# Nota: Rs2 se ignora (operación unaria), típicamente se usa R0
# Flags: Z, N, P
# Uso: Rd = ~Rs1 (complemento a uno)
# -----------------------------------------------------------------------------

MOVI R0, 0
NOT R3, R8, R0              # R3 = ~42 (complemento a uno de 64 bits)

# -----------------------------------------------------------------------------
# SHL - Shift Left (Desplazamiento lógico a la izquierda)
# -----------------------------------------------------------------------------
# Sintaxis: SHL Rd, Rs1, Rs2
# Codificación: Opcode=0x18
# Flags: Z, N, P
# Uso: Rd = Rs1 << (Rs2 & 63)
# Nota: Solo se usan los 6 bits menos significativos de Rs2 (0-63)
# -----------------------------------------------------------------------------

MOVI R4, 3
SHL R11, R8, R4             # R11 = 42 << 3 = 336

# -----------------------------------------------------------------------------
# SHR - Shift Right (Desplazamiento lógico a la derecha)
# -----------------------------------------------------------------------------
# Sintaxis: SHR Rd, Rs1, Rs2
# Codificación: Opcode=0x19
# Flags: Z, N, P
# Uso: Rd = Rs1 >> (Rs2 & 63) (desplazamiento sin signo)
# Nota: Solo se usan los 6 bits menos significativos de Rs2
# -----------------------------------------------------------------------------

SHR R12, R11, R4            # R12 = 336 >> 3 = 42

# -----------------------------------------------------------------------------
# ADDI - Add Immediate (Suma con inmediato)
# -----------------------------------------------------------------------------
# Sintaxis: ADDI Rd, Rs1, #imm32
# Codificación: Opcode=0x20
# Flags: Z, N, P, C, V
# Uso: Rd = Rs1 + sign_extend(imm32)
# Nota: El inmediato se extiende con signo de 32 a 64 bits
# -----------------------------------------------------------------------------

ADDI R13, R8, -10           # R13 = 42 + (-10) = 32
ADDI R14, R8, 100           # R14 = 42 + 100 = 142

# ===============================================================================
# 3. INSTRUCCIONES DE PUNTO FLOTANTE (R-Type, IEEE 754 Double Precision)
# ===============================================================================

# -----------------------------------------------------------------------------
# FADD - Floating Add (Suma de punto flotante)
# -----------------------------------------------------------------------------
# Sintaxis: FADD Rd, Rs1, Rs2
# Codificación: Opcode=0x1A
# Flags: Z, N, P, V (si resultado es infinito)
# Uso: Rd = Rs1 + Rs2 (suma IEEE 754 double precision)
# Nota: Los registros contienen representación binaria de doubles
# -----------------------------------------------------------------------------

FADD R15, R5, R6            # R15 = 3.5 + 2.0 = 5.5

# -----------------------------------------------------------------------------
# FSUB - Floating Subtract (Resta de punto flotante)
# -----------------------------------------------------------------------------
# Sintaxis: FSUB Rd, Rs1, Rs2
# Codificación: Opcode=0x1B
# Flags: Z, N, P, V
# Uso: Rd = Rs1 - Rs2
# -----------------------------------------------------------------------------

FSUB R1, R5, R6             # R1 = 3.5 - 2.0 = 1.5

# -----------------------------------------------------------------------------
# FMUL - Floating Multiply (Multiplicación de punto flotante)
# -----------------------------------------------------------------------------
# Sintaxis: FMUL Rd, Rs1, Rs2
# Codificación: Opcode=0x1C
# Flags: Z, N, P, V
# Uso: Rd = Rs1 * Rs2
# -----------------------------------------------------------------------------

FMUL R2, R5, R6             # R2 = 3.5 * 2.0 = 7.0

# -----------------------------------------------------------------------------
# FDIV - Floating Divide (División de punto flotante)
# -----------------------------------------------------------------------------
# Sintaxis: FDIV Rd, Rs1, Rs2
# Codificación: Opcode=0x1D
# Flags: Z, N, P, V (si división por cero → infinito)
# Uso: Rd = Rs1 / Rs2
# Nota: División por 0.0 resulta en ±inf según IEEE 754
# -----------------------------------------------------------------------------

FDIV R3, R5, R6             # R3 = 3.5 / 2.0 = 1.75
OUT R3, 0xFFFF0008, 6       # Imprime 1.75
OUT R10, 0xFFFF0000         # Newline

# ===============================================================================
# 4. INSTRUCCIONES DE ACCESO A MEMORIA (I-Type)
# ===============================================================================

# -----------------------------------------------------------------------------
# LD - Load (Cargar desde memoria)
# -----------------------------------------------------------------------------
# Sintaxis: LD Rd, address        (absoluto, FUNC=0)
#           LD Rd, Rs1, offset    (relativo, FUNC=1)
# Codificación: Opcode=0x23
#   FUNC=0: IMM32 = dirección absoluta
#   FUNC=1: dirección = Rs1 + sign_extend(IMM32)
# Flags: No afecta
# Uso: Cargar palabra de 64 bits desde memoria a registro
# -----------------------------------------------------------------------------

# LD absoluto: dirección directa o etiqueta
LD R11, valor_a              # R11 = memoria[valor_a]

# LD relativo: base + offset
MOVI R4, base_area           # R4 = dirección de base_area
LD R12, R4, 0                # R12 = memoria[base_area + 0]
LD R13, R4, 8                # R13 = memoria[base_area + 8]

# -----------------------------------------------------------------------------
# ST - Store (Almacenar en memoria)
# -----------------------------------------------------------------------------
# Sintaxis: ST Rs, address        (absoluto, FUNC=0)
#           ST Rs, Rb, offset     (relativo, FUNC=1)
# Codificación: Opcode=0x24
#   FUNC=0: IMM32 = dirección absoluta
#   FUNC=1: dirección = Rb + sign_extend(IMM32)
# Flags: No afecta
# Uso: Almacenar palabra de 64 bits desde registro a memoria
# -----------------------------------------------------------------------------

# ST absoluto
ST R8, valor_a               # memoria[valor_a] = R8 (42)

# ST relativo
ST R1, R4, 16                # memoria[base_area + 16] = R1
ST R2, R4, 24                # memoria[base_area + 24] = R2

# ===============================================================================
# 5. INSTRUCCIONES DE PILA Y SUBRUTINAS
# ===============================================================================

# -----------------------------------------------------------------------------
# PUSH - Push to Stack (Empujar a la pila)
# -----------------------------------------------------------------------------
# Sintaxis: PUSH Rs             (registro, FUNC=1)
#           PUSH #imm32         (inmediato, FUNC=0)
# Codificación: Opcode=0x50
# Flags: No afecta
# Uso: SP = SP - 8; memoria[SP] = Rs o imm32
# Nota: Crece hacia direcciones menores
# -----------------------------------------------------------------------------

PUSH R8                      # Empuja 42 a la pila
PUSH R1                      # Empuja R1 a la pila
MOVI R9, 999
PUSH R9                      # Empuja 999 a la pila (desde registro)

# -----------------------------------------------------------------------------
# POP - Pop from Stack (Sacar de la pila)
# -----------------------------------------------------------------------------
# Sintaxis: POP Rd
# Codificación: Opcode=0x51
# Flags: No afecta
# Uso: Rd = memoria[SP]; SP = SP + 8
# -----------------------------------------------------------------------------

POP R14                      # R14 = valor del tope de la pila (999)
POP R15                      # R15 = siguiente valor

# -----------------------------------------------------------------------------
# CALL - Call Subroutine (Llamar a subrutina)
# -----------------------------------------------------------------------------
# Sintaxis: CALL address
# Codificación: Opcode=0x46, IMM32=dirección destino
# Flags: No afecta
# Uso: PUSH(PC+8); PC = address
# Nota: Guarda dirección de retorno automáticamente
# -----------------------------------------------------------------------------

CALL subrutina_inc           # Llama a subrutina

# -----------------------------------------------------------------------------
# RET - Return from Subroutine (Retornar de subrutina)
# -----------------------------------------------------------------------------
# Sintaxis: RET
# Codificación: Opcode=0x47
# Flags: No afecta
# Uso: PC = POP()
# Nota: Recupera dirección de retorno de la pila
# -----------------------------------------------------------------------------
# Ver implementación en subrutina_inc más abajo

# ===============================================================================
# 6. INSTRUCCIONES DE COMPARACIÓN Y CONTROL DE FLUJO
# ===============================================================================

# -----------------------------------------------------------------------------
# CMP - Compare (Comparar registros)
# -----------------------------------------------------------------------------
# Sintaxis: CMP Rd, Rs1, Rs2   (forma completa)
#           CMP Rs1, Rs2       (forma abreviada, Rd=R0)
# Codificación: Opcode=0x30
# Flags: Z, N, P, C, V (según Rs1 - Rs2)
# Uso: Realiza Rs1 - Rs2 y actualiza flags sin guardar resultado
# Nota: Típicamente se usa la forma abreviada para comparaciones
# -----------------------------------------------------------------------------

CMP R8, R1                   # Compara R8 - R1 (42 - valor), actualiza flags

# -----------------------------------------------------------------------------
# JMP - Jump Unconditional (Salto incondicional)
# -----------------------------------------------------------------------------
# Sintaxis: JMP address
# Codificación: Opcode=0x40, IMM32=dirección destino
# Flags: No afecta
# Uso: PC = address
# -----------------------------------------------------------------------------

JMP despues_saltos           # Salta incondicionalmente

# -----------------------------------------------------------------------------
# JZ - Jump if Zero (Saltar si cero)
# -----------------------------------------------------------------------------
# Sintaxis: JZ address
# Codificación: Opcode=0x41
# Flags: Lee Z
# Uso: Si Z=1 entonces PC = address
# Condición: Resultado anterior fue cero (igualdad en CMP)
# -----------------------------------------------------------------------------

etiqueta_test_jz:
CMP R8, R8                   # R8 - R8 = 0, setea Z=1
JZ etiqueta_z_set            # Salta porque Z=1

# -----------------------------------------------------------------------------
# JNZ - Jump if Not Zero (Saltar si no cero)
# -----------------------------------------------------------------------------
# Sintaxis: JNZ address
# Codificación: Opcode=0x42
# Flags: Lee Z
# Uso: Si Z=0 entonces PC = address
# Condición: Resultado anterior no fue cero (desigualdad en CMP)
# -----------------------------------------------------------------------------

etiqueta_z_set:
CMP R8, R1                   # Compara valores diferentes
JNZ etiqueta_nz_set          # Salta si son diferentes (Z=0)

# -----------------------------------------------------------------------------
# JC - Jump if Carry (Saltar si carry)
# -----------------------------------------------------------------------------
# Sintaxis: JC address
# Codificación: Opcode=0x43
# Flags: Lee C
# Uso: Si C=1 entonces PC = address
# Condición: Hubo acarreo en operación aritmética anterior
# -----------------------------------------------------------------------------

etiqueta_nz_set:
MOVI R11, 0x7FFFFFFF
ADDI R11, R11, 0x7FFFFFFF    # Genera overflow/carry
JC etiqueta_carry_set        # Salta si C=1

# -----------------------------------------------------------------------------
# JNC - Jump if Not Carry (Saltar si no carry)
# -----------------------------------------------------------------------------
# Sintaxis: JNC address
# Codificación: Opcode=0x44
# Flags: Lee C
# Uso: Si C=0 entonces PC = address
# -----------------------------------------------------------------------------

etiqueta_carry_set:
MOVI R12, 10
ADDI R12, R12, 5             # No genera carry
JNC etiqueta_no_carry        # Salta si C=0

# -----------------------------------------------------------------------------
# JS - Jump if Signed (Saltar si negativo)
# -----------------------------------------------------------------------------
# Sintaxis: JS address
# Codificación: Opcode=0x45
# Flags: Lee N
# Uso: Si N=1 entonces PC = address
# Condición: Resultado anterior fue negativo (bit de signo = 1)
# Uso típico: Detectar números negativos en aritmética con signo
# -----------------------------------------------------------------------------

etiqueta_no_carry:
MOVI R13, -100
CMP R0, R13, R0              # Compara -100 con 0, setea N=1
JS etiqueta_negativo         # Salta porque N=1

etiqueta_negativo:
despues_saltos:
OUT R10, 0xFFFF0000          # Newline

# ===============================================================================
# 7. INSTRUCCIONES DE ENTRADA/SALIDA AVANZADAS
# ===============================================================================

# -----------------------------------------------------------------------------
# IN - Input (Entrada desde puerto/MMIO)
# -----------------------------------------------------------------------------
# Sintaxis: IN Rd, port[, FUNC]           (básico)
#           IN Rd, Rs1, count             (extendido para arrays)
# Codificación: Opcode=0x60
# FUNC básico bits [3:1] = subop:
#   0: Entero con signo normal
#   3: Flotante (double precision)
# FUNC extendido:
#   subop=1: Parse array de enteros (Rs1=base, IMM32=count)
#   bits [11:4] = separador ASCII (típicamente 0x20 para espacio)
# Flags: No afecta
# Uso básico: Leer un valor desde consola/puerto
# Uso extendido: Leer múltiples enteros de una línea a memoria
# -----------------------------------------------------------------------------

# IN básico de entero (descomentar para uso interactivo)
# IN R11, 0xFFFF0018          # Lee un entero desde consola a R11
# OUT R11, 0xFFFF0008         # Imprime el valor leído
# OUT R10, 0xFFFF0000         # Newline

# IN de flotante con FUNC=6 (subop=3)
# IN R12, 0xFFFF0018, 6       # Lee un double desde consola a R12
# OUT R12, 0xFFFF0008, 6      # Imprime el flotante
# OUT R10, 0xFFFF0000         # Newline

# IN extendido para arrays: lee múltiples enteros separados por espacios
# Ejemplo: leer 5 números en una línea como "10 20 30 40 50"
# MOVI R13, array_datos       # R13 = dirección base del array
# IN R14, R13, 5              # Lee 5 enteros a memoria[R13..R13+32]
#                             # R14 = cantidad de números parseados
# FUNC se codifica automáticamente como ((0x20)<<4)|(1<<1) = 514

# -----------------------------------------------------------------------------
# INS - Input String (Entrada de string)
# -----------------------------------------------------------------------------
# Sintaxis: INS Rd, port
# Codificación: Opcode=0x62, Rd contiene dirección del buffer
# Flags: No afecta
# Uso: Lee una línea completa desde puerto a buffer en memoria
# Nota: Agrega terminador null automáticamente
# -----------------------------------------------------------------------------

MOVI R4, buffer              # R4 = dirección del buffer
# INS R4, 0xFFFF0018          # Lee línea a buffer (descomentar para interactivo)

# -----------------------------------------------------------------------------
# OUTS - Output String (Salida de string)
# -----------------------------------------------------------------------------
# Sintaxis: OUTS Rs, port
# Codificación: Opcode=0x63, Rs contiene dirección del string
# Flags: No afecta
# Uso: Imprime string null-terminated desde memoria
# -----------------------------------------------------------------------------

OUTS R4, 0xFFFF0008          # Imprime string desde buffer
OUT R10, 0xFFFF0000          # Newline

# -----------------------------------------------------------------------------
# OUT con arrays (demostración de subops)
# -----------------------------------------------------------------------------
# OUT con array signed: FUNC = (sep<<4)|(1<<1)
# Ejemplo: imprimir 4 enteros con espacio de separador
MOVI R5, array_datos
MOVI R6, 1
MOVI R7, 2
MOVI R8, 3
ST R6, R5, 0
ST R7, R5, 8
ST R8, R5, 16
ST R6, R5, 24
OUT R5, 4, 514               # Imprime 4 enteros con espacio (514 = (32<<4)|(1<<1))
OUT R10, 0xFFFF0000          # Newline

# OUT con array unsigned: FUNC = (sep<<4)|(5<<1) = 522
# Útil para evitar mostrar negativos en aritmética que hace wrap
MOVI R9, -1                  # -1 en complemento a 2 = 0xFFFFFFFFFFFFFFFF
ST R9, R5, 0
OUT R5, 1, 522               # Imprime como unsigned: 18446744073709551615
OUT R10, 0xFFFF0000          # Newline

# ===============================================================================
# 8. INSTRUCCIONES DE SISTEMA (S-Type)
# ===============================================================================

# -----------------------------------------------------------------------------
# NOP - No Operation (Sin operación)
# -----------------------------------------------------------------------------
# Sintaxis: NOP
# Codificación: Opcode=0x70
# Flags: No afecta
# Uso: No hace nada, consume un ciclo
# Aplicaciones: Alineación, timing, relleno de pipeline
# -----------------------------------------------------------------------------

NOP
NOP
NOP

# -----------------------------------------------------------------------------
# HALT - Halt Execution (Detener ejecución)
# -----------------------------------------------------------------------------
# Sintaxis: HALT
# Codificación: Opcode=0x71
# Flags: No afecta
# Uso: Detiene la CPU, finaliza el programa
# Nota: La ejecución no continúa después de HALT
# -----------------------------------------------------------------------------

HALT

# ===============================================================================
# 9. SUBRUTINAS Y ÁREA DE DATOS
# ===============================================================================

subrutina_inc:
    # Ejemplo de subrutina simple: incrementa R1
    ADDI R1, R1, 1           # R1 = R1 + 1
    RET                      # Retorna al llamador

# ===============================================================================
# ÁREA DE DATOS
# ===============================================================================

# -----------------------------------------------------------------------------
# Directivas de datos:
#   DW (Define Word): Define palabras de 64 bits
#   DB (Define Byte): Define bytes (strings y datos byte)
#   RESW (Reserve Words): Reserva espacio sin inicializar
#   ORG (Origin): Establece la dirección de ensamblado
# -----------------------------------------------------------------------------

valor_a: DW 0                # Variable de 64 bits inicializada en 0

# Área para pruebas de LD/ST relativo (4 palabras = 32 bytes)
base_area:
    DW 0
    DW 0
    DW 0
    DW 0

# Array para pruebas de entrada/salida
array_datos:
    DW 0
    DW 0
    DW 0
    DW 0
    DW 0

# Buffer para strings
# Reservamos espacio para un string (palabra alineada)
buffer:
    DW 0
    DW 0
    DW 0
    DW 0

# ===============================================================================
# RESUMEN DE TIPOS DE INSTRUCCIÓN
# ===============================================================================
#
# R-Type (Registro-Registro):
#   ADD, SUB, MUL, DIV, AND, OR, XOR, NOT, SHL, SHR, CMP
#   FADD, FSUB, FMUL, FDIV
#   Formato: OP Rd, Rs1, Rs2
#
# I-Type (Inmediato/Memoria):
#   MOVI, ADDI, LD, ST, CP, PUSH, POP
#   IN, OUT, INS, OUTS
#   Formato: OP Rd, Rs1, #imm / OP Rd, #imm
#
# J-Type (Saltos):
#   JMP, JZ, JNZ, JC, JNC, JS, CALL, RET
#   Formato: OP address
#
# S-Type (Sistema):
#   NOP, HALT
#   Formato: OP
#
# ===============================================================================
# CONVENCIONES DE CODIFICACIÓN
# ===============================================================================
#
# Registros: R0-R15 (64 bits cada uno)
# Inmediatos: Números decimales, hexadecimales (0x...), o flotantes (con punto)
# Etiquetas: Identificadores seguidos de ':' para marcar posiciones
# Comentarios: Inician con '#' y van hasta el final de la línea
#
# Direccionamiento:
#   - Absoluto: usa etiquetas o direcciones directas
#   - Relativo: base + offset (3 operandos en LD/ST)
#   - Inmediato: constantes embebidas en la instrucción
#
# ===============================================================================
