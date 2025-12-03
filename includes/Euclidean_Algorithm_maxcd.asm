FUNC_maxcd:
    POP R14
    POP R0
    ST R0, [maxcd_param_c_1]
    POP R0
    ST R0, [maxcd_param_d_2]
    PUSH R14
    maxcd_L11:
    LD R0, [maxcd_param_c_1]
    PUSH R0
    LD R0, [maxcd_param_d_2]
    POP R1
    CMP R1, R0
    JNZ maxcd_L3
    MOVI R0, 0
    JMP maxcd_L4
    maxcd_L3:
    MOVI R0, 1
    maxcd_L4:
    MOVI R1, 0
    CMP R0, R1
    JZ maxcd_L12
    LD R0, [maxcd_param_c_1]
    PUSH R0
    LD R0, [maxcd_param_d_2]
    POP R1
    CMP R1, R0
    JS maxcd_L8_false
    JZ maxcd_L8_false
    JMP maxcd_L6
    maxcd_L8_false:
    MOVI R0, 0
    JMP maxcd_L7
    maxcd_L6:
    MOVI R0, 1
    maxcd_L7:
    MOVI R1, 0
    CMP R0, R1
    JZ maxcd_L9
    LD R0, [maxcd_param_c_1]
    PUSH R0
    LD R0, [maxcd_param_d_2]
    POP R1
    SUB R0, R1, R0
    ST R0, [maxcd_param_c_1]
    JMP maxcd_L10
    maxcd_L9:
    LD R0, [maxcd_param_d_2]
    PUSH R0
    LD R0, [maxcd_param_c_1]
    POP R1
    SUB R0, R1, R0
    ST R0, [maxcd_param_d_2]
    maxcd_L10:
    JMP maxcd_L11
    maxcd_L12:
    LD R0, [maxcd_param_c_1]
    RET

    maxcd_param_c_1: DW 0
    maxcd_param_d_2: DW 0

