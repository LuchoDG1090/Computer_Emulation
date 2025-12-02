ORG 0
JMP __MAIN

FUNC_bubble_sort:
    POP R14
    POP R0
    ST R0, [param_arr_1]
    POP R0
    ST R0, [param_n_2]
    PUSH R14
    MOVI R0, 0
    ST R0, [var_i_3]
    MOVI R0, 0
    ST R0, [var_j_4]
    MOVI R0, 1
    ST R0, [var_swapped_5]
    MOVI R0, 0
    ST R0, [var_tmp_6]

L20:
    LD R0, [var_swapped_5]
    PUSH R0
    MOVI R0, 0
    POP R1
    CMP R1, R0
    JNZ L7
    MOVI R0, 0
    JMP L8

L7:
    MOVI R0, 1

L8:
    MOVI R1, 0
    CMP R0, R1
    JZ L21
    MOVI R0, 0
    ST R0, [var_swapped_5]
    MOVI R0, 1
    ST R0, [var_i_3]

L18:
    LD R0, [var_i_3]
    PUSH R0
    LD R0, [param_n_2]
    POP R1
    CMP R1, R0
    JS L10
    MOVI R0, 0
    JMP L11

L10:
    MOVI R0, 1

L11:
    MOVI R1, 0
    CMP R0, R1
    JZ L19
    LD R0, [var_i_3]
    PUSH R0
    MOVI R0, 1
    POP R1
    SUB R0, R1, R0
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [param_arr_1]
    ADD R15, R2, R1
    LD R0, R15, 0
    PUSH R0
    LD R0, [var_i_3]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [param_arr_1]
    ADD R15, R2, R1
    LD R0, R15, 0
    POP R1
    CMP R1, R0
    JS L15_false
    JZ L15_false
    JMP L13

L15_false:
    MOVI R0, 0
    JMP L14

L13:
    MOVI R0, 1

L14:
    MOVI R1, 0
    CMP R0, R1
    JZ L17
    LD R0, [var_i_3]
    PUSH R0
    MOVI R0, 1
    POP R1
    SUB R0, R1, R0
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [param_arr_1]
    ADD R15, R2, R1
    LD R0, R15, 0
    ST R0, [var_tmp_6]
    LD R0, [var_i_3]
    PUSH R0
    MOVI R0, 1
    POP R1
    SUB R0, R1, R0
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [param_arr_1]
    ADD R15, R2, R1
    PUSH R15
    LD R0, [var_i_3]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [param_arr_1]
    ADD R15, R2, R1
    LD R0, R15, 0
    POP R15
    ST R0, R15, 0
    LD R0, [var_i_3]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [param_arr_1]
    ADD R15, R2, R1
    PUSH R15
    LD R0, [var_tmp_6]
    POP R15
    ST R0, R15, 0
    MOVI R0, 1
    ST R0, [var_swapped_5]

L17:
    LD R0, [var_i_3]
    PUSH R0
    MOVI R0, 1
    POP R1
    ADD R0, R1, R0
    ST R0, [var_i_3]
    JMP L18

L19:
    LD R0, [param_n_2]
    PUSH R0
    MOVI R0, 1
    POP R1
    SUB R0, R1, R0
    ST R0, [param_n_2]
    JMP L20

L21:
    RET

__MAIN:
    HALT

param_arr_1: DW 0
param_n_2: DW 0
var_i_3: DW 0
var_j_4: DW 0
var_swapped_5: DW 0
var_tmp_6: DW 0
__HEAP_PTR: DW __HEAP_START
__HEAP_START: DW 0