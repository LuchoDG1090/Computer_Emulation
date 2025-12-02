FUNC_bubble_sort:
    POP R14
    POP R0
    ST R0, [bubble_sort_arr]
    POP R0
    ST R0, [bubble_sort_n]
    PUSH R14
    MOVI R0, 0
    ST R0, [bubble_sort_i]
    MOVI R0, 0
    ST R0, [bubble_sort_j]
    MOVI R0, 1
    ST R0, [bubble_sort_swapped]
    MOVI R0, 0
    ST R0, [bubble_sort_tmp]
    bubble_sort_L20:
    LD R0, [bubble_sort_swapped]
    PUSH R0
    MOVI R0, 0
    POP R1
    CMP R1, R0
    JNZ bubble_sort_L7
    MOVI R0, 0
    JMP bubble_sort_L8
    bubble_sort_L7:
    MOVI R0, 1
    bubble_sort_L8:
    MOVI R1, 0
    CMP R0, R1
    JZ bubble_sort_L21
    MOVI R0, 0
    ST R0, [bubble_sort_swapped]
    MOVI R0, 1
    ST R0, [bubble_sort_i]
    bubble_sort_L18:
    LD R0, [bubble_sort_i]
    PUSH R0
    LD R0, [bubble_sort_n]
    POP R1
    CMP R1, R0
    JS bubble_sort_L10
    MOVI R0, 0
    JMP bubble_sort_L11
    bubble_sort_L10:
    MOVI R0, 1
    bubble_sort_L11:
    MOVI R1, 0
    CMP R0, R1
    JZ bubble_sort_L19
    LD R0, [bubble_sort_i]
    PUSH R0
    MOVI R0, 1
    POP R1
    SUB R0, R1, R0
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [bubble_sort_arr]
    ADD R15, R2, R1
    LD R0, R15, 0
    PUSH R0
    LD R0, [bubble_sort_i]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [bubble_sort_arr]
    ADD R15, R2, R1
    LD R0, R15, 0
    POP R1
    CMP R1, R0
    JS bubble_sort_L15_false
    JZ bubble_sort_L15_false
    JMP bubble_sort_L13
    bubble_sort_L15_false:
    MOVI R0, 0
    JMP bubble_sort_L14
    bubble_sort_L13:
    MOVI R0, 1
    bubble_sort_L14:
    MOVI R1, 0
    CMP R0, R1
    JZ bubble_sort_L17
    LD R0, [bubble_sort_i]
    PUSH R0
    MOVI R0, 1
    POP R1
    SUB R0, R1, R0
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [bubble_sort_arr]
    ADD R15, R2, R1
    LD R0, R15, 0
    ST R0, [bubble_sort_tmp]
    LD R0, [bubble_sort_i]
    PUSH R0
    MOVI R0, 1
    POP R1
    SUB R0, R1, R0
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [bubble_sort_arr]
    ADD R15, R2, R1
    PUSH R15
    LD R0, [bubble_sort_i]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [bubble_sort_arr]
    ADD R15, R2, R1
    LD R0, R15, 0
    POP R15
    ST R0, R15, 0
    LD R0, [bubble_sort_i]
    MOVI R1, 8
    MUL R1, R0, R1
    LD R2, [bubble_sort_arr]
    ADD R15, R2, R1
    PUSH R15
    LD R0, [bubble_sort_tmp]
    POP R15
    ST R0, R15, 0
    MOVI R0, 1
    ST R0, [bubble_sort_swapped]
    bubble_sort_L17:
    LD R0, [bubble_sort_i]
    PUSH R0
    MOVI R0, 1
    POP R1
    ADD R0, R1, R0
    ST R0, [bubble_sort_i]
    JMP bubble_sort_L18
    bubble_sort_L19:
    LD R0, [bubble_sort_n]
    PUSH R0
    MOVI R0, 1
    POP R1
    SUB R0, R1, R0
    ST R0, [bubble_sort_n]
    JMP bubble_sort_L20
    bubble_sort_L21:
    RET

    bubble_sort_arr: DW 0
    bubble_sort_n: DW 0
    bubble_sort_i: DW 0
    bubble_sort_j: DW 0
    bubble_sort_swapped: DW 0
    bubble_sort_tmp: DW 0
