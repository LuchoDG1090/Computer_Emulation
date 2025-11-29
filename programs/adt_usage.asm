ORG 0
JMP __MAIN

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