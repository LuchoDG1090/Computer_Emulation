ORG 0
JMP __MAIN
FUNC_Point_setSecret:
POP R14
POP R0
ST R0, [param_this_1]
POP R0
ST R0, [param_value_2]
PUSH R14
LD R0, [param_value_2]
LD R1, [param_this_1]
ST R0, R1, 0
RET
FUNC_Point_printSecret:
POP R14
POP R0
ST R0, [param_this_3]
PUSH R14
LD R1, [param_this_3]
LD R0, R1, 0
OUT R0, 0xFFFF0008
RET
FUNC_Point_sethola:
POP R14
POP R0
ST R0, [param_this_4]
POP R0
ST R0, [param_value_5]
PUSH R14
LD R0, [param_value_5]
LD R1, [param_this_4]
ST R0, R1, 24
RET
FUNC_Point_printhola:
POP R14
POP R0
ST R0, [param_this_6]
PUSH R14
LD R1, [param_this_6]
LD R0, R1, 24
OUT R0, 0xFFFF0008
RET
__MAIN:
MOVI R0, 10
ST R0, adt_p_7_x
MOVI R0, 20
ST R0, adt_p_7_y
LD R0, [adt_p_7_x]
OUT R0, 0xFFFF0008
LD R0, [adt_p_7_y]
OUT R0, 0xFFFF0008
MOVI R0, 40
PUSH R0
MOVI R0, adt_p_7
PUSH R0
CALL FUNC_Point_setSecret
MOVI R0, adt_p_7
PUSH R0
CALL FUNC_Point_printSecret
MOVI R0, 70
PUSH R0
MOVI R0, adt_p_7
PUSH R0
CALL FUNC_Point_sethola
MOVI R0, adt_p_7
PUSH R0
CALL FUNC_Point_printhola
HALT

param_this_1: DW 0
param_value_2: DW 0
param_this_3: DW 0
param_this_4: DW 0
param_value_5: DW 0
param_this_6: DW 0
adt_p_7:
adt_p_7_secret: DW 0
adt_p_7_x: DW 0
adt_p_7_y: DW 0
adt_p_7_hola: DW 0
__HEAP_PTR: DW __HEAP_START
__HEAP_START: DW 0