FUNC_mat_mul:
    POP R14
    POP R0
    ST R0, [mat_mul_param_A_1]
    POP R0
    ST R0, [mat_mul_param_B_2]
    POP R0
    ST R0, [mat_mul_param_C_3]
    POP R0
    ST R0, [mat_mul_param_rowsA_4]
    POP R0
    ST R0, [mat_mul_param_colsA_5]
    POP R0
    ST R0, [mat_mul_param_colsB_6]
    PUSH R14
    MOVI R0, 0
    ST R0, [mat_mul_var_i_7]
    MOVI R0, 0
    ST R0, [mat_mul_var_j_8]
    MOVI R0, 0
    ST R0, [mat_mul_var_k_9]
    MOVI R0, 0
    ST R0, [mat_mul_var_sum_10]
    MOVI R0, 0
    ST R0, [mat_mul_var_idxA_11]
    MOVI R0, 0
    ST R0, [mat_mul_var_idxB_12]
    MOVI R0, 0
    ST R0, [mat_mul_var_idxC_13]
    MOVI R0, 0
    ST R0, [mat_mul_var_i_7]
    mat_mul_L27:
    LD R0, [mat_mul_var_i_7]
    PUSH R0
    LD R0, [mat_mul_param_rowsA_4]
    POP R1
    CMP R1, R0
    JS mat_mul_L14
    MOVI R0, 0
    JMP mat_mul_L15
    mat_mul_L14:
    MOVI R0, 1
    mat_mul_L15:
    MOVI R1, 0
    CMP R0, R1
    JZ mat_mul_L28
    MOVI R0, 0
    ST R0, [mat_mul_var_j_8]
    mat_mul_L25:
    LD R0, [mat_mul_var_j_8]
    PUSH R0
    LD R0, [mat_mul_param_colsB_6]
    POP R1
    CMP R1, R0
    JS mat_mul_L17
    MOVI R0, 0
    JMP mat_mul_L18
    mat_mul_L17:
    MOVI R0, 1
    mat_mul_L18:
    MOVI R1, 0
    CMP R0, R1
    JZ mat_mul_L26
    MOVI R0, 0
    ST R0, [mat_mul_var_sum_10]
    MOVI R0, 0
    ST R0, [mat_mul_var_k_9]
    mat_mul_L23:
    LD R0, [mat_mul_var_k_9]
    PUSH R0
    LD R0, [mat_mul_param_colsA_5]
    POP R1
    CMP R1, R0
    JS mat_mul_L20
    MOVI R0, 0
    JMP mat_mul_L21
    mat_mul_L20:
    MOVI R0, 1
    mat_mul_L21:
    MOVI R1, 0
    CMP R0, R1
    JZ mat_mul_L24
    LD R0, [mat_mul_var_i_7]
    PUSH R0
    LD R0, [mat_mul_param_colsA_5]
    POP R1
    MUL R0, R1, R0
    PUSH R0
    LD R0, [mat_mul_var_k_9]
    POP R1
    ADD R0, R1, R0
    ST R0, [mat_mul_var_idxA_11]
    LD R0, [mat_mul_var_k_9]
    PUSH R0
    LD R0, [mat_mul_param_colsB_6]
    POP R1
    MUL R0, R1, R0
    PUSH R0
    LD R0, [mat_mul_var_j_8]
    POP R1
    ADD R0, R1, R0
    ST R0, [mat_mul_var_idxB_12]
    LD R0, [mat_mul_var_sum_10]
    PUSH R0
    LD R0, [mat_mul_var_idxA_11]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [mat_mul_param_A_1]
    ADD R15, R2, R1
    LD R0, R15, 0
    PUSH R0
    LD R0, [mat_mul_var_idxB_12]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [mat_mul_param_B_2]
    ADD R15, R2, R1
    LD R0, R15, 0
    POP R1
    MUL R0, R1, R0
    POP R1
    ADD R0, R1, R0
    ST R0, [mat_mul_var_sum_10]
    LD R0, [mat_mul_var_k_9]
    PUSH R0
    MOVI R0, 1
    POP R1
    ADD R0, R1, R0
    ST R0, [mat_mul_var_k_9]
    JMP mat_mul_L23
    mat_mul_L24:
    LD R0, [mat_mul_var_i_7]
    PUSH R0
    LD R0, [mat_mul_param_colsB_6]
    POP R1
    MUL R0, R1, R0
    PUSH R0
    LD R0, [mat_mul_var_j_8]
    POP R1
    ADD R0, R1, R0
    ST R0, [mat_mul_var_idxC_13]
    LD R0, [mat_mul_var_idxC_13]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [mat_mul_param_C_3]
    ADD R15, R2, R1
    PUSH R15
    LD R0, [mat_mul_var_sum_10]
    POP R15
    ST R0, R15, 0
    LD R0, [mat_mul_var_j_8]
    PUSH R0
    MOVI R0, 1
    POP R1
    ADD R0, R1, R0
    ST R0, [mat_mul_var_j_8]
    JMP mat_mul_L25
    mat_mul_L26:
    LD R0, [mat_mul_var_i_7]
    PUSH R0
    MOVI R0, 1
    POP R1
    ADD R0, R1, R0
    ST R0, [mat_mul_var_i_7]
    JMP mat_mul_L27
    mat_mul_L28:
    RET

    mat_mul_param_A_1: DW 0
    mat_mul_param_B_2: DW 0
    mat_mul_param_C_3: DW 0
    mat_mul_param_rowsA_4: DW 0
    mat_mul_param_colsA_5: DW 0
    mat_mul_param_colsB_6: DW 0
    mat_mul_var_i_7: DW 0
    mat_mul_var_j_8: DW 0
    mat_mul_var_k_9: DW 0
    mat_mul_var_sum_10: DW 0
    mat_mul_var_idxA_11: DW 0
    mat_mul_var_idxB_12: DW 0
    mat_mul_var_idxC_13: DW 0

