import ply.yacc as yacc
from lexer import tokens 

# ----------------------------------------
# 1. ESTRUCTURA DEL PROGRAMA
# ----------------------------------------

#Las {} representan repetición

def p_program(p):
    """program : declaration program
            | func_decl program
            | adt_decl program
            | declaration
            | func_decl
            | adt_decl """
    pass

# ----------------------------------------
# 2. TIPOS DE DATOS
# ----------------------------------------

def p_type(p):
    """type : INT
            | FLOAT
            | STRING
            | BOOL
            | CHAR
            | VOID  """
    pass

# ----------------------------------------
# 3. DECLARACIONES
# ----------------------------------------

#Los [] representan ser opcionales, en ese caso se tuvieron que crear mas funciones
#para representar que sean opcionales

def p_declaration(p): 
    """declaration : type ID array_opc init_opc"""
    pass

def p_array_opc(p):
    """array_opc : array_suffix
            | """
    pass

def p_init_opc(p):
    """init_opc : ASSIGN exp
            | """
    pass

def p_array_suffix(p):
    """array_suffix : LBRACKET exp RBRACKET array_suffix
            |  LBRACKET exp RBRACKET """
    pass

# ----------------------------------------
# 4. FUNCIONES
# ----------------------------------------

def p_func_decl(p):
    """func_decl : FUNC ID LPAREN param_list RPAREN COLON block ENDFUNC"""
    pass

def p_param_list(p):
    """param_list : param"""
    pass

def p_param(p):
    """param : type ID param_opc"""
    pass

def p_param_opc(p):
    """param_opc : array_suffix
            | """
    pass


# ----------------------------------------
# 5. ADTs (TIPOS ABSTRACTOS DE DATOS)
# ----------------------------------------

def p_adt_decl(p):
    """adt_decl : ADT ID LPAREN param_list RPAREN COLON atd_body ENDADT"""
    pass

def p_adt_body(p):
    """adt_body : visibility_block adt_body
            | attribute_decl adt_body
            | func_decl atd_body
            | visibility_block
            | attribute_decl
            | func_decl 
            """
    pass

def p_visibility_block(p):
    """visibility_block : PRIVATE COLON block
            | PUBLIC COLON block"""
    pass

def p_attribute_decl(p):
    """attribute_decl : type ID array_opc"""
    pass

# ----------------------------------------
# 6. BLOQUES Y SENTENCIAS
# ----------------------------------------

def p_block(p):
    """block : statement"""
    pass

def p_statement(p):
    """statement :   declaration 
    | assign_stmt
    | if_stmt
    | while_stmt           
    | for_stmt             
    | func_call            
    | return_stmt          
    | BREAK             
    | CONTINUE           
    | output_stmt          
    | input_stmt """
    pass

# ----------------------------------------
# 7. ASIGNACIÓN
# ----------------------------------------

def p_assign_stmt(p):
    """assign_stmt : lvalue ASSIGN exp """
    pass

def p_lvalue(p):
    """lvalue : ID lvalue2"""
    pass

def p_lvalue2(p):
    """lvalue2 : LBRACKET exp RBRACKET lvalue2
            | '.' ID lvalue2
            | """
    pass

# ----------------------------------------
# 8. ENTRADA / SALIDA
# ----------------------------------------

def output_stmt(p):
    """output_smtm : OUTPUT exp"""
    pass

def input_stmt(p):
    """input_stmt : INPUT lvalue"""
    pass

# ----------------------------------------
# 9. ESTRUCTURAS DE CONTROL
# ----------------------------------------

def if_stmt(p):
    """if_stmt : IF LPAREN exp RPAREN COLON block else_opc ENDIF"""
    pass

def else_opc(p):
    """else_opc : ELSE COLON block
        | """
    pass

def while_stmt(p):
    """while_stmt : WHILE LPAREN exp RPAREN COLON block ENDWHILE"""
    pass

