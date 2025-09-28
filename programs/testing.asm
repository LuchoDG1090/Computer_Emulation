ORG 0x0000
start:
    LD R1, [A]
    IN R1, 0xFFFF0018
    OUT R1, 0xFFFF0008
    ADDI  R1, R1, 1
    CP R2, R1
    OUT R2, 0xFFFF0008
    ST R1, [B]
    JMP mcd

mcd:
    HALT

# Datos
ORG 0x0BB8             # 3000 decimal
A:  DW 12              # variable A en 0x0BB8 con valor inicial 12
B:  RESW 1             # reserva una palabra para B (inicializada a 0)