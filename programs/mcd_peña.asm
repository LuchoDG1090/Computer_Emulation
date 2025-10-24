# ---------- Código ----------
ORG 2500
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
ORG 375
a: RESW 1               # reserva una palabra para a (inicializada en 0)

ORG 1535
b: RESW 1               # reserva una palabra para b (inicializada en 0)

ORG 7478
res: RESW 1             # reserva una palabra para el resultado (inicializada en 0)

# ---------- Strings (usando directiva DB) ----------
ORG 0xF000
msg1: DB "Ingrese el primer numero: ", 0
msg2: DB "Ingrese el segundo numero: ", 0
msg_result: DB "El MCD es: ", 0