import ply.yacc as yacc
from lexer import tokens 

# ----------------------------------------
# 1. ESTRUCTURA DEL PROGRAMA
# ----------------------------------------

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
    """init_opc : '=' exp
            | """
    pass

def p_array_suffix(p):
    """array_suffix : '[' exp ']' array_suffix
            |  '[' exp ']' """
    pass

# ----------------------------------------
# 4. FUNCIONES
# ----------------------------------------

def p_func_decl(p):
    """func_decl : FUNC ID '(' param_list ')' ':' block ENDFUNC"""
    pass

def p_param_list(p):
    """param_list : param ',' param"""
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
    """adt_decl : ADT ID '(' param_list ')' ':' atd_body ENDADT  """
    pass

def p_adt_body(p):
    """adt_body : visibility_block adt_body
            | attribute_decl adt_body
            | func_decl atd_body
            | visibiluty_block
            | atribute_decl
            | func_decl 
            """
    pass

def p_visibility_block(p):
    """visibility_block : PRIVATE : block
            | PULIC : block"""
    pass

def p_attribute_decl(p):
    """atribute_decl : type ID array_opc"""
    pass

# ----------------------------------------
# 6. BLOQUES Y SENTENCIAS
# ----------------------------------------

