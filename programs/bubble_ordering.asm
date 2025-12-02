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
MOVI R0, STR_1
OUTS R0, 0xFFFF0008
MOVI R0, 0
ST R0, [var_n_22]
IN R0, 0xFFFF0018
ST R0, [var_n_22]
                LD R0, [var_n_22]
                MOVI R1, 8
                MUL R0, R0, R1
                LD R1, [__HEAP_PTR]
                ST R1, [arr_arr_23]
                ADD R1, R1, R0
                ST R1, [__HEAP_PTR]
MOVI R0, STR_2
OUTS R0, 0xFFFF0008
MOVI R0, 0
ST R0, [var_k_24]
MOVI R0, 0
ST R0, [var_val_25]
L29:
LD R0, [var_k_24]
PUSH R0
LD R0, [var_n_22]
POP R1
CMP R1, R0
JS L26
MOVI R0, 0
JMP L27
L26:
MOVI R0, 1
L27:
MOVI R1, 0
CMP R0, R1
JZ L30
IN R0, 0xFFFF0018
ST R0, [var_val_25]
LD R0, [var_k_24]
MOVI R1, 8
MUL R1, R0, R1
LD R2, [arr_arr_23]
ADD R15, R2, R1
PUSH R15
LD R0, [var_val_25]
POP R15
ST R0, R15, 0
LD R0, [var_k_24]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_k_24]
JMP L29
L30:
LD R0, [var_n_22]
PUSH R0
LD R0, [arr_arr_23]
PUSH R0
CALL FUNC_bubble_sort
MOVI R0, STR_3
OUTS R0, 0xFFFF0008
MOVI R0, 0
ST R0, [var_k_24]
L34:
LD R0, [var_k_24]
PUSH R0
LD R0, [var_n_22]
POP R1
CMP R1, R0
JS L31
MOVI R0, 0
JMP L32
L31:
MOVI R0, 1
L32:
MOVI R1, 0
CMP R0, R1
JZ L35
LD R0, [var_k_24]
MOVI R1, 8
MUL R1, R0, R1
LD R2, [arr_arr_23]
ADD R15, R2, R1
LD R0, R15, 0
OUT R0, 0xFFFF0008, 4
MOVI R0, STR_4
OUTS R0, 0xFFFF0008
LD R0, [var_k_24]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_k_24]
JMP L34
L35:
MOVI R0, STR_5
OUTS R0, 0xFFFF0008
HALT

param_arr_1: DW 0
param_n_2: DW 0
var_i_3: DW 0
var_j_4: DW 0
var_swapped_5: DW 0
var_tmp_6: DW 0
STR_1: DB "Ingrese la cantidad de elementos:", 0
var_n_22: DW 0
arr_arr_23: DW 0
STR_2: DB "Ingrese los elementos separados por espacio:", 0
var_k_24: DW 0
var_val_25: DW 0
STR_3: DB "Arreglo ordenado:", 0
STR_4: DB " ", 0
STR_5: DB "\n", 0
__HEAP_PTR: DW __HEAP_START

__HEAP_START: DW 0
