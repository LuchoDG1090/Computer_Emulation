# ---------- Código ----------
ORG 0x4E20              # 20.000 en hexadecimal, correspondiente a la posición 2.500 en la memoria (8 bytes)
entrada:
    IN R4, 0xFFFF0018
    ST R4, [a]

    IN R4, 0xFFFF0018
    ST R4, [b]

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
    OUT R1, 0xFFFF0008
    HALT

# ---------- Datos ----------
ORG 0x0BB8              # 3.000 en hexadecimal, correspondiente a la posición 375 en la memoria (8 bytes)
a: RESW 1               # reserva una palabra para a (inicializada en 0)

ORG 0x2FF8              # 12.280 en hexadecimal, correspondiente a la posición 1.535 en la memoria (8 bytes)
b: RESW 1               # reserva una palabra para b (inicializada en 0)

ORG 0xE9B0              # 59.824 en hexadecimal, correspondiente a la posición 7.478 en la memoria (8 bytes)
res: RESW 1             # reserva una palabra para el resultado (inicializada en 0)