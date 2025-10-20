# ---------- Código ----------
ORG 0x4E20              # 20.000 en hexadecimal, correspondiente a la posición 2.500 en la memoria (8 bytes)
entrada:
    # Imprimir mensaje "Ingrese el primer número: "
    MOVI R5, msg1       # Cargar dirección del mensaje en R5
    OUTS R5, 0xFFFF0008 # Imprimir string a consola
    IN R4, 0xFFFF0018   # Leer número
    ST R4, [a]          # Guardar en variable 'a'

    # Imprimir mensaje "Ingrese el segundo número: "
    MOVI R5, msg2       # Cargar dirección del segundo mensaje
    OUTS R5, 0xFFFF0008 # Imprimir string a consola
    IN R4, 0xFFFF0018   # Leer número
    ST R4, [b]          # Guardar en variable 'b'

mcd:
    LD R1, [a]
    LD R2, [b]

bucle:
    CP R3, R1
    SUB R3, R3, R2
    JZ fin
    JS menor
    SUB R1, R1, R2
    JMP bucle

menor:
    SUB R2, R2, R1
    JMP bucle

fin:
    ST R1, [res]
    
    # Imprimir mensaje "El MCD es: "
    MOVI R5, msg_result
    OUTS R5, 0xFFFF0008
    
    OUT R1, 0xFFFF0008  # Imprimir el resultado
    HALT

# ---------- Datos ----------
ORG 0x0BB8              # 3.000 en hexadecimal, correspondiente a la posición 375 en la memoria (8 bytes)
a: RESW 1               # reserva una palabra para a (inicializada en 0)

ORG 0x2FF8              # 12.280 en hexadecimal, correspondiente a la posición 1.535 en la memoria (8 bytes)
b: RESW 1               # reserva una palabra para b (inicializada en 0)

ORG 0xE9B0              # 59.824 en hexadecimal, correspondiente a la posición 7.478 en la memoria (8 bytes)
res: RESW 1             # reserva una palabra para el resultado (inicializada en 0)

# ---------- Strings (usando directiva DB) ----------
ORG 0xF000              # Strings en una posición alta de memoria (61440 bytes, dentro del rango de 64KB)
msg1: DB "Ingrese el primer numero: ", 0
msg2: DB "Ingrese el segundo numero: ", 0
msg_result: DB "El MCD es: ", 0