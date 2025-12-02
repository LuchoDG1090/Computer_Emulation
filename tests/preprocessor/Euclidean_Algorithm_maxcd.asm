ORG 0
JMP __MAIN

FUNC_maxcd:
    POP R14
    POP R0
    ST R0, [param_a0_1]
    POP R0
    ST R0, [param_b0_2]
    PUSH R14
    LD R0, [param_a0_1]
    ST R0, [var_a_3]
    LD R0, [param_b0_2]
    ST R0, [var_b_4]

L13:
    LD R0, [var_a_3]
    PUSH R0
    LD R0, [var_b_4]
    POP R1
    CMP R1, R0
    JNZ L5
    MOVI R0, 0
    JMP L6

L5:
    MOVI R0, 1

L6:
    MOVI R1, 0
    CMP R0, R1
    JZ L14
    LD R0, [var_a_3]
    PUSH R0
    LD R0, [var_b_4]
    POP R1
    CMP R1, R0
    JS L10_false
    JZ L10_false
    JMP L8

L10_false:
    MOVI R0, 0
    JMP L9

L8:
    MOVI R0, 1

L9:
    MOVI R1, 0
    CMP R0, R1
    JZ L11
    LD R0, [var_a_3]
    PUSH R0
    LD R0, [var_b_4]
    POP R1
    SUB R0, R1, R0
    ST R0, [var_a_3]
    JMP L12

L11:
    LD R0, [var_b_4]
    PUSH R0
    LD R0, [var_a_3]
    POP R1
    SUB R0, R1, R0
    ST R0, [var_b_4]

L12:
    JMP L13

L14:
    LD R0, [var_a_3]
    RET

__MAIN:
    RET
    HALT

param_a0_1: DW 0
param_b0_2: DW 0
var_a_3: DW 0
var_b_4: DW 0
__HEAP_PTR: DW __HEAP_START
__HEAP_START: DW 0