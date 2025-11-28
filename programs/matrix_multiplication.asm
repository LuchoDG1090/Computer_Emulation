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
MOVI R0, 3
ST R0, [var_rowsA_29]
MOVI R0, 2
ST R0, [var_colsA_30]
MOVI R0, 2
ST R0, [var_rowsB_31]
MOVI R0, 4
ST R0, [var_colsB_32]
MOVI R0, STR_1
OUTS R0, 0xFFFF0008
MOVI R0, STR_2
OUTS R0, 0xFFFF0008
MOVI R0, 0
ST R0, [var_row_36]
MOVI R0, 0
ST R0, [var_col_37]
MOVI R0, 0
ST R0, [var_temp_38]
MOVI R0, 0
ST R0, [var_idx_39]
MOVI R0, 0
ST R0, [var_row_36]
L48:
LD R0, [var_row_36]
PUSH R0
LD R0, [var_rowsA_29]
POP R1
CMP R1, R0
JS L40
MOVI R0, 0
JMP L41
L40:
MOVI R0, 1
L41:
MOVI R1, 0
CMP R0, R1
JZ L49
MOVI R0, 0
ST R0, [var_col_37]
L46:
LD R0, [var_col_37]
PUSH R0
LD R0, [var_colsA_30]
POP R1
CMP R1, R0
JS L43
MOVI R0, 0
JMP L44
L43:
MOVI R0, 1
L44:
MOVI R1, 0
CMP R0, R1
JZ L47
IN R0, 0xFFFF0018
ST R0, [var_temp_38]
LD R0, [var_row_36]
PUSH R0
LD R0, [var_colsA_30]
POP R1
MUL R0, R1, R0
PUSH R0
LD R0, [var_col_37]
POP R1
ADD R0, R1, R0
ST R0, [var_idx_39]
LD R0, [var_idx_39]
MOVI R1, 8
MUL R1, R0, R1
MOVI R2, arr_A_33
ADD R15, R2, R1
PUSH R15
LD R0, [var_temp_38]
POP R15
ST R0, R15, 0
LD R0, [var_col_37]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_col_37]
JMP L46
L47:
LD R0, [var_row_36]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_row_36]
JMP L48
L49:
MOVI R0, STR_3
OUTS R0, 0xFFFF0008
MOVI R0, STR_4
OUTS R0, 0xFFFF0008
MOVI R0, 0
ST R0, [var_row_36]
L58:
LD R0, [var_row_36]
PUSH R0
LD R0, [var_rowsB_31]
POP R1
CMP R1, R0
JS L50
MOVI R0, 0
JMP L51
L50:
MOVI R0, 1
L51:
MOVI R1, 0
CMP R0, R1
JZ L59
MOVI R0, 0
ST R0, [var_col_37]
L56:
LD R0, [var_col_37]
PUSH R0
LD R0, [var_colsB_32]
POP R1
CMP R1, R0
JS L53
MOVI R0, 0
JMP L54
L53:
MOVI R0, 1
L54:
MOVI R1, 0
CMP R0, R1
JZ L57
IN R0, 0xFFFF0018
ST R0, [var_temp_38]
LD R0, [var_row_36]
PUSH R0
LD R0, [var_colsB_32]
POP R1
MUL R0, R1, R0
PUSH R0
LD R0, [var_col_37]
POP R1
ADD R0, R1, R0
ST R0, [var_idx_39]
LD R0, [var_idx_39]
MOVI R1, 8
MUL R1, R0, R1
MOVI R2, arr_B_34
ADD R15, R2, R1
PUSH R15
LD R0, [var_temp_38]
POP R15
ST R0, R15, 0
LD R0, [var_col_37]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_col_37]
JMP L56
L57:
LD R0, [var_row_36]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_row_36]
JMP L58
L59:
MOVI R0, STR_5
OUTS R0, 0xFFFF0008
MOVI R0, 0
ST R0, [var_row_36]
L68:
LD R0, [var_row_36]
PUSH R0
LD R0, [var_rowsA_29]
POP R1
CMP R1, R0
JS L60
MOVI R0, 0
JMP L61
L60:
MOVI R0, 1
L61:
MOVI R1, 0
CMP R0, R1
JZ L69
MOVI R0, 0
ST R0, [var_col_37]
L66:
LD R0, [var_col_37]
PUSH R0
LD R0, [var_colsA_30]
POP R1
CMP R1, R0
JS L63
MOVI R0, 0
JMP L64
L63:
MOVI R0, 1
L64:
MOVI R1, 0
CMP R0, R1
JZ L67
LD R0, [var_row_36]
PUSH R0
LD R0, [var_colsA_30]
POP R1
MUL R0, R1, R0
PUSH R0
LD R0, [var_col_37]
POP R1
ADD R0, R1, R0
ST R0, [var_idx_39]
LD R0, [var_idx_39]
MOVI R1, 8
MUL R1, R0, R1
MOVI R2, arr_A_33
ADD R15, R2, R1
LD R0, R15, 0
OUT R0, 0xFFFF0008, 4
MOVI R0, STR_6
OUTS R0, 0xFFFF0008
LD R0, [var_col_37]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_col_37]
JMP L66
L67:
MOVI R0, STR_7
OUTS R0, 0xFFFF0008
LD R0, [var_row_36]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_row_36]
JMP L68
L69:
MOVI R0, STR_8
OUTS R0, 0xFFFF0008
MOVI R0, 0
ST R0, [var_row_36]
L78:
LD R0, [var_row_36]
PUSH R0
LD R0, [var_rowsB_31]
POP R1
CMP R1, R0
JS L70
MOVI R0, 0
JMP L71
L70:
MOVI R0, 1
L71:
MOVI R1, 0
CMP R0, R1
JZ L79
MOVI R0, 0
ST R0, [var_col_37]
L76:
LD R0, [var_col_37]
PUSH R0
LD R0, [var_colsB_32]
POP R1
CMP R1, R0
JS L73
MOVI R0, 0
JMP L74
L73:
MOVI R0, 1
L74:
MOVI R1, 0
CMP R0, R1
JZ L77
LD R0, [var_row_36]
PUSH R0
LD R0, [var_colsB_32]
POP R1
MUL R0, R1, R0
PUSH R0
LD R0, [var_col_37]
POP R1
ADD R0, R1, R0
ST R0, [var_idx_39]
LD R0, [var_idx_39]
MOVI R1, 8
MUL R1, R0, R1
MOVI R2, arr_B_34
ADD R15, R2, R1
LD R0, R15, 0
OUT R0, 0xFFFF0008, 4
MOVI R0, STR_9
OUTS R0, 0xFFFF0008
LD R0, [var_col_37]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_col_37]
JMP L76
L77:
MOVI R0, STR_10
OUTS R0, 0xFFFF0008
LD R0, [var_row_36]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_row_36]
JMP L78
L79:
LD R0, [var_colsB_32]
PUSH R0
LD R0, [var_colsA_30]
PUSH R0
LD R0, [var_rowsA_29]
PUSH R0
MOVI R0, arr_C_35
PUSH R0
MOVI R0, arr_B_34
PUSH R0
MOVI R0, arr_A_33
PUSH R0
CALL FUNC_mat_mul
MOVI R0, STR_11
OUTS R0, 0xFFFF0008
MOVI R0, 0
ST R0, [var_r_80]
MOVI R0, 0
ST R0, [var_c_81]
MOVI R0, 0
ST R0, [var_pos_82]
MOVI R0, 0
ST R0, [var_r_80]
L91:
LD R0, [var_r_80]
PUSH R0
LD R0, [var_rowsA_29]
POP R1
CMP R1, R0
JS L83
MOVI R0, 0
JMP L84
L83:
MOVI R0, 1
L84:
MOVI R1, 0
CMP R0, R1
JZ L92
MOVI R0, 0
ST R0, [var_c_81]
L89:
LD R0, [var_c_81]
PUSH R0
LD R0, [var_colsB_32]
POP R1
CMP R1, R0
JS L86
MOVI R0, 0
JMP L87
L86:
MOVI R0, 1
L87:
MOVI R1, 0
CMP R0, R1
JZ L90
LD R0, [var_r_80]
PUSH R0
LD R0, [var_colsB_32]
POP R1
MUL R0, R1, R0
PUSH R0
LD R0, [var_c_81]
POP R1
ADD R0, R1, R0
ST R0, [var_pos_82]
LD R0, [var_pos_82]
MOVI R1, 8
MUL R1, R0, R1
MOVI R2, arr_C_35
ADD R15, R2, R1
LD R0, R15, 0
OUT R0, 0xFFFF0008, 4
MOVI R0, STR_12
OUTS R0, 0xFFFF0008
LD R0, [var_c_81]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_c_81]
JMP L89
L90:
MOVI R0, STR_13
OUTS R0, 0xFFFF0008
LD R0, [var_r_80]
PUSH R0
MOVI R0, 1
POP R1
ADD R0, R1, R0
ST R0, [var_r_80]
JMP L91
L92:
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
var_rowsA_29: DW 0
var_colsA_30: DW 0
var_rowsB_31: DW 0
var_colsB_32: DW 0
arr_A_33: DW 0 0 0 0 0 0
arr_B_34: DW 0 0 0 0 0 0 0 0
arr_C_35: DW 0 0 0 0 0 0 0 0 0 0 0 0
STR_1: DB "Ingrese la matriz A (3x2), una fila por linea (2 numeros separados por espacio):", 0
STR_2: DB "\n", 0
var_row_36: DW 0
var_col_37: DW 0
var_temp_38: DW 0
var_idx_39: DW 0
STR_3: DB "Ingrese la matriz B (2x4), una fila por linea (4 numeros separados por espacio):", 0
STR_4: DB "\n", 0
STR_5: DB "Matriz A:\n", 0
STR_6: DB " ", 0
STR_7: DB "\n", 0
STR_8: DB "Matriz B:\n", 0
STR_9: DB " ", 0
STR_10: DB "\n", 0
STR_11: DB "Matriz C = A x B:\n", 0
var_r_80: DW 0
var_c_81: DW 0
var_pos_82: DW 0
STR_12: DB " ", 0
STR_13: DB "\n", 0
__HEAP_PTR: DW __HEAP_START
__HEAP_START: DW 0