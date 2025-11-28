ORG 0
MOVI R0, 10
ST R0, [var_x_1]
MOVI R0, 3.14159
ST R0, [var_pi_2]
MOVI R0, STR_1
ST R0, [var_mensaje_3]
MOVI R0, 1
ST R0, [var_activo_4]
HALT

var_x_1: DW 0
var_pi_2: DW 0
STR_1: DB "Hola mundo \t\r\u", 0
var_mensaje_3: DW 0
var_activo_4: DW 0
__HEAP_PTR: DW __HEAP_START
__HEAP_START: DW 0