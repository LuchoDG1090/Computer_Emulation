ORG 0
JMP __MAIN
FUNC_maxcd:
POP R14
POP R0
ST R0, [param_c_1]
POP R0
ST R0, [param_d_2]
PUSH R14
L11:
LD R0, [param_c_1]
PUSH R0
LD R0, [param_d_2]
POP R1
CMP R1, R0
JNZ L3
MOVI R0, 0
JMP L4
L3:
MOVI R0, 1
L4:
MOVI R1, 0
CMP R0, R1
JZ L12
LD R0, [param_c_1]
PUSH R0
LD R0, [param_d_2]
POP R1
CMP R1, R0
JS L8_false
JZ L8_false
JMP L6
L8_false:
MOVI R0, 0
JMP L7
L6:
MOVI R0, 1
L7:
MOVI R1, 0
CMP R0, R1
JZ L9
LD R0, [param_c_1]
PUSH R0
LD R0, [param_d_2]
POP R1
SUB R0, R1, R0
ST R0, [param_c_1]
JMP L10
L9:
LD R0, [param_d_2]
PUSH R0
LD R0, [param_c_1]
POP R1
SUB R0, R1, R0
ST R0, [param_d_2]
L10:
JMP L11
L12:
LD R0, [param_c_1]
RET
__MAIN:
MOVI R0, STR_1
OUTS R0, 0xFFFF0008
IN R0, 0xFFFF0018
ST R0, [var_a_13]
MOVI R0, STR_2
OUTS R0, 0xFFFF0008
IN R0, 0xFFFF0018
ST R0, [var_b_14]
LD R0, [var_b_14]
PUSH R0
LD R0, [var_a_13]
PUSH R0
CALL FUNC_maxcd
ST R0, [var_a_13]
MOVI R0, STR_3
OUTS R0, 0xFFFF0008
LD R0, [var_a_13]
OUT R0, 0xFFFF0008
HALT

param_c_1: DW 0
param_d_2: DW 0
var_a_13: DW 0
STR_1: DB "Ingrese el primer numero: ", 0
var_b_14: DW 0
STR_2: DB "Ingrese el segundo numero: ", 0
STR_3: DB "El resultado es: ", 0
__HEAP_PTR: DW __HEAP_START
__HEAP_START: DW 0