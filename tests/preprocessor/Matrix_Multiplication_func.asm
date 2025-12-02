ORG 0
JMP __MAIN

FUNC_mat_mul:
    POP R14
    POP R0
    ST R0, [param_A_1]
    POP R0
    ST R0, [param_B_2]
    POP R0
    ST R0, [param_C_3]
    POP R0
    ST R0, [param_rowsA_4]
    POP R0
    ST R0, [param_colsA_5]
    POP R0
    ST R0, [param_colsB_6]
    PUSH R14
    MOVI R0, 0
    ST R0, [var_i_7]
    MOVI R0, 0
    ST R0, [var_j_8]
    MOVI R0, 0
    ST R0, [var_k_9]
    MOVI R0, 0
    ST R0, [var_sum_10]
    MOVI R0, 0
    ST R0, [var_idxA_11]
    MOVI R0, 0
    ST R0, [var_idxB_12]
    MOVI R0, 0
    ST R0, [var_idxC_13]
    MOVI R0, 0
    ST R0, [var_i_7]

L27:
    LD R0, [var_i_7]
    PUSH R0
    LD R0, [param_rowsA_4]
    POP R1
    CMP R1, R0
    JS L14
    MOVI R0, 0
    JMP L15

L14:
    MOVI R0, 1

L15:
    MOVI R1, 0
    CMP R0, R1
    JZ L28
    MOVI R0, 0
    ST R0, [var_j_8]

L25:
    LD R0, [var_j_8]
    PUSH R0
    LD R0, [param_colsB_6]
    POP R1
    CMP R1, R0
    JS L17
    MOVI R0, 0
    JMP L18

L17:
    MOVI R0, 1

L18:
    MOVI R1, 0
    CMP R0, R1
    JZ L26
    MOVI R0, 0
    ST R0, [var_sum_10]
    MOVI R0, 0
    ST R0, [var_k_9]

L23:
    LD R0, [var_k_9]
    PUSH R0
    LD R0, [param_colsA_5]
    POP R1
    CMP R1, R0
    JS L20
    MOVI R0, 0
    JMP L21

L20:
    MOVI R0, 1

L21:
    MOVI R1, 0
    CMP R0, R1
    JZ L24
    LD R0, [var_i_7]
    PUSH R0
    LD R0, [param_colsA_5]
    POP R1
    MUL R0, R1, R0
    PUSH R0
    LD R0, [var_k_9]
    POP R1
    ADD R0, R1, R0
    ST R0, [var_idxA_11]
    LD R0, [var_k_9]
    PUSH R0
    LD R0, [param_colsB_6]
    POP R1
    MUL R0, R1, R0
    PUSH R0
    LD R0, [var_j_8]
    POP R1
    ADD R0, R1, R0
    ST R0, [var_idxB_12]
    LD R0, [var_sum_10]
    PUSH R0
    LD R0, [var_idxA_11]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [param_A_1]
    ADD R15, R2, R1
    LD R0, R15, 0
    PUSH R0
    LD R0, [var_idxB_12]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [param_B_2]
    ADD R15, R2, R1
    LD R0, R15, 0
    POP R1
    MUL R0, R1, R0
    POP R1
    ADD R0, R1, R0
    ST R0, [var_sum_10]
    LD R0, [var_k_9]
    PUSH R0
    MOVI R0, 1
    POP R1
    ADD R0, R1, R0
    ST R0, [var_k_9]
    JMP L23

L24:
    LD R0, [var_i_7]
    PUSH R0
    LD R0, [param_colsB_6]
    POP R1
    MUL R0, R1, R0
    PUSH R0
    LD R0, [var_j_8]
    POP R1
    ADD R0, R1, R0
    ST R0, [var_idxC_13]
    LD R0, [var_idxC_13]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [param_C_3]
    ADD R15, R2, R1
    PUSH R15
    LD R0, [var_sum_10]
    POP R15
    ST R0, R15, 0
    LD R0, [var_j_8]
    PUSH R0
    MOVI R0, 1
    POP R1
    ADD R0, R1, R0
    ST R0, [var_j_8]
    JMP L25

L26:
    LD R0, [var_i_7]
    PUSH R0
    MOVI R0, 1
    POP R1
    ADD R0, R1, R0
    ST R0, [var_i_7]
    JMP L27

L28:
    RET

__MAIN:
    HALT

param_A_1: DW 0
param_B_2: DW 0
param_C_3: DW 0
param_rowsA_4: DW 0
param_colsA_5: DW 0
param_colsB_6: DW 0
var_i_7: DW 0
var_j_8: DW 0
var_k_9: DW 0
var_sum_10: DW 0
var_idxA_11: DW 0
var_idxB_12: DW 0
var_idxC_13: DW 0
__HEAP_PTR: DW __HEAP_START
__HEAP_START: DW 0