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
    """param_list : param
           | param_list COMMA param"""
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
    """adt_decl : ADT ID LPAREN param_list RPAREN COLON adt_body ENDADT"""
    pass

def p_adt_body(p):
    """adt_body : visibility_block adt_body
            | attribute_decl adt_body
            | func_decl adt_body
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
    """block : statement block
        | """
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

def p_output_stmt(p):
    """output_stmt : OUTPUT exp"""
    pass

def p_input_stmt(p):
    """input_stmt : INPUT lvalue"""
    pass

# ----------------------------------------
# 9. ESTRUCTURAS DE CONTROL
# ----------------------------------------

def p_if_stmt(p):
    """if_stmt : IF LPAREN exp RPAREN COLON block else_opc ENDIF"""
    pass

def p_else_opc(p):
    """else_opc : ELSE COLON block
        | """
    pass

def p_while_stmt(p):
    """while_stmt : WHILE LPAREN exp RPAREN COLON block ENDWHILE"""
    pass

def p_for_stmt(p):
    """for_stmt : FOR LPAREN ID IN range RPAREN COLON block ENDFOR"""
    pass

def p_return_stmt(p):
    """return_stmt : RETURN exp_opc"""
    pass
def p_exp_opc(p):
    """exp_opc : exp
        | """
    pass
def p_range(p):
    """range : exp RANGE exp"""


# ----------------------------------------
# 10. LLAMADAS A FUNCIONES
# ----------------------------------------

def p_func_call(p):
    """func_call : ID LPAREN ar_list_opt RPAREN"""
    pass

def p_arg_list(p):
    """arg_list : exp
        | arg_list COMMA exp"""
    pass

# ----------------------------------------
# 11. EXPRESIONES
# ----------------------------------------

def p_exp(p):
    """exp : logical_or_exp"""
    pass

def p_logical_or_exp(p):
    """logical_or_exp : logical_and_exp 
        | logical_or_exp OR logical_and_exp """
    pass

def p_logical_and_exp(p):
    """logical_and_exp : bitwise_or_exp
        | bitwise_or_exp AND bitwise_or_exp"""
    pass

def p_bitwise_or_exp(p):
    """bitwise_or_exp : bitwise_xor_exp
        | bitwise_or_exp BIT_OR bitwise_xor_exp"""
    pass

def p_bitwise_xor_exp(p):
    """bitwise_xor_exp : bitwise_and_exp
                       | bitwise_xor_exp BIT_XOR bitwise_and_exp"""
    pass

def p_bitwise_and_exp(p):
    """bitwise_and_exp : equality_exp
                       | bitwise_and_exp BIT_AND equality_exp"""
    pass

def p_equality_exp(p):
    """equality_exp : relational_exp
                    | equality_exp EQ relational_exp
                    | equality_exp NEQ relational_exp"""
    pass

def p_relational_exp(p):
    """relational_exp : shift_exp
                      | relational_exp LT shift_exp
                      | relational_exp LE shift_exp
                      | relational_exp GT shift_exp
                      | relational_exp GE shift_exp"""
    pass


def p_shift_exp(p):
    """shift_exp : additive_exp
                 | shift_exp SHIFT_LEFT additive_exp
                 | shift_exp SHIFT_RIGHT additive_exp"""
    pass

def p_additive_exp(p):
    """additive_exp : multiplicative_exp
                    | additive_exp PLUS multiplicative_exp
                    | additive_exp MINUS multiplicative_exp"""
    pass

def p_multiplicative_exp(p):
    """multiplicative_exp : power_exp
                          | multiplicative_exp TIMES power_exp
                          | multiplicative_exp DIVIDE power_exp
                          | multiplicative_exp MOD power_exp"""
    pass

def p_power_exp(p):
    """power_exp : unary_exp
                 | unary_exp POWER unary_exp"""
    pass

def p_unary_exp(p):
    """unary_exp : primary_exp
                 | NOT unary_exp
                 | PLUS unary_exp
                 | MINUS unary_exp
                 | BIT_NOT unary_exp
                 | INCREMENT unary_exp
                 | DECREMENT unary_exp"""
    pass

def p_primary_exp(p):
    """primary_exp : INTEGER              
                | FLOAT               
                | STRING               
                | TRUE                 
                | FALSE              
                | lvalue               
                | func_call            
                | adt_constructor      
                | LPAREN exp RPAREN ;        
"""
    pass

def p_adt_constructor(p):
    """adt_constructor : ID '(' opt_arg_list ')'"""
    pass


def p_error(p):
    print("Syntax error")

parser = yacc.yacc()



