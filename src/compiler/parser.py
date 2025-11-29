import sys
import os

# Añadir directorio src al path para permitir 'import ply.yacc'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import ply.yacc as yacc

class MyParser:
    def __init__(self, tokens, library_functions=None):
        self.tokens = tokens
        self.parser = yacc.yacc(module=self)
        self.library_functions = library_functions if library_functions else set()
        self.called_functions = set()

        # Tabla de símbolos: nombre -> {
        #   'type': <nombre_tipo>,
        #   'label': <etiqueta_memoria>,
        #   'is_array': bool,
        #   'array_size': int|None,
        #   'is_adt': bool
        # }
        self.symbol_table = {}

        # Sección de datos: lista de líneas para emitir después de HALT
        self.data_section = []

        # Contador de etiquetas para etiquetas únicas
        self.label_count = 0
        
        # Contador de cadenas para etiquetas de sección de datos
        self.string_count = 0

        # Tabla de Tipos TDA: {
        #   'NombreTDA': {
        #       'members': { 'nombreMiembro': {'visibility': 'public'|'private', 'offset': int} },
        #       'operations': { 'nombreOp': {'visibility': vis, 'params': [...], 'body': <asm o alto-nivel>} },
        #       'size': <conteo_miembros>
        #   }
        # }
        self.type_table = {}

        # Contexto actual: None o nombre de TDA mientras se parsea una operación TDA
        self.current_context = None
        self.current_adt_members = {}
        self.current_adt_offset = 0

        # Pila de bucles para break/continue
        self.loop_stack = []

        # Ensamblador acumulado para un parseo
        self.asm = ""
        
        # Contador de errores
        self.error_count = 0

    # Generador de etiquetas de utilidad usado por la nueva lógica de declaración
    def _new_label(self, prefix: str):
        self.label_count += 1
        return f"{prefix}_{self.label_count}"

    def _error(self, msg, p):
        print(f"[Error del Parser] {msg}")
        self.error_count += 1
        
    def get_new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    # ----------------------------------------
    # Precedencia
    # ----------------------------------------
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'BIT_OR'),
        ('left', 'BIT_XOR'),
        ('left', 'BIT_AND'),
        ('left', 'EQ', 'NEQ'),
        ('left', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'SHIFT_LEFT', 'SHIFT_RIGHT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD'),
        ('right', 'NOT', 'BIT_NOT', 'INCREMENT', 'DECREMENT'), # Unario
    )

    # ==========================================================================
    # 1. ESTRUCTURA DEL PROGRAMA
    # ==========================================================================
    
    def p_program(self, p):
        """program : statements"""
        code, ast = p[1]
        
        # Añadir Puntero al Heap
        self.data_section.append("__HEAP_PTR: DW __HEAP_START")
        self.data_section.append("__HEAP_START: DW 0")
        
        data_section_str = "\n".join(self.data_section)
        
        # Si no hay funciones definidas, todo es código principal
        if 'FUNC_' not in code:
             p[0] = (f"ORG 0\n{code}\nHALT\n\n{data_section_str}", {"type": "Program", "body": ast})
             return

        # Separar funciones del código principal
        lines = code.split('\n')
        functions = []
        main_code = []
        in_function = False
        
        for line in lines:
            stripped = line.strip()
            # Detectar inicio de función
            if stripped.startswith('FUNC_'):
                in_function = True
            
            if in_function:
                functions.append(line)
                # Detectar fin de función (RET)
                if stripped == 'RET':
                    in_function = False
            elif stripped: # Líneas que no son funciones ni vacías van al main
                main_code.append(line)
        
        func_section = "\n".join(functions)
        main_section = "\n".join(main_code)
        
        p[0] = (f"ORG 0\nJMP __MAIN\n{func_section}\n__MAIN:\n{main_section}\nHALT\n\n{data_section_str}", {"type": "Program", "body": ast})

    def p_statements(self, p):
        """statements : statement statements
                      | statement"""
        if len(p) == 3:
            s1_code, s1_ast = p[1]
            s2_code, s2_ast = p[2]
            
            if isinstance(s2_ast, list):
                final_ast = [s1_ast] + s2_ast
            else:
                final_ast = [s1_ast, s2_ast]
                
            p[0] = (f"{s1_code}\n{s2_code}", final_ast)
        else:
            s1_code, s1_ast = p[1]
            p[0] = (s1_code, [s1_ast])

    # ==========================================================================
    # 5. SENTENCIAS
    # ==========================================================================

    def p_statement(self, p):
        """statement : declaration
                     | assignment
                     | expression SEMI
                     | if_stmt
                     | while_stmt
                     | for_stmt
                     | output_stmt
                     | input_stmt
                     | func_decl
                     | return_stmt
                     | func_call_stmt
                     | break_stmt
                     | continue_stmt
                     | adt_decl"""
        if p[1] is None:
            p[0] = ("", None)
        elif isinstance(p[1], tuple):
            # Handle expression tuple (code, type, ast)
            if len(p[1]) == 3:
                p[0] = (p[1][0], p[1][2])
            else:
                p[0] = p[1]
        else:
            p[0] = (p[1], None)

    # ==========================================================================
    # 2. DECLARACIONES
    # ==========================================================================
    def p_declaration(self, p):
        """declaration : type ID SEMI
                        | type ID ASSIGN expression SEMI
                        | type ID LBRACKET expression RBRACKET SEMI"""
        var_type = p[1]
        name = p[2]
        is_init = len(p) == 6 and p[3] == '='
        is_array_decl = len(p) == 7 and p[3] == '['

        if name in self.symbol_table:
            self._error(f"Identificador '{name}' ya declarado", p)

        # Declaración con inicialización
        if is_init:
            label = self._new_label(f"var_{name}")
            self.symbol_table[name] = {
                'label': label,
                'type': var_type,
                'is_array': False,
                'is_adt': False
            }
            self.data_section.append(f"{label}: DW 0")
            expr = p[4]
            expr_code = expr[0]
            expr_ast = expr[2]
            p[0] = (f"{expr_code}\nST R0, [{label}]", {"type": "Declaration", "var_type": var_type, "name": name, "init": expr_ast})
            return

        # Declaración de instancia TDA (el tipo existe en type_table)
        if var_type in self.type_table:
            adt_info = self.type_table[var_type]
            instance_label = self._new_label(f"adt_{name}")
            
            # Etiqueta base para la instancia (bloque de memoria contiguo)
            self.data_section.append(f"{instance_label}:")
            
            member_map = {}
            data_lines = []
            # Espera miembros almacenados como: adt_info['members'] = { memberName: { 'visibility': ..., 'type': <type>, 'offset': int } }
            for m_name, meta in adt_info['members'].items():
                mem_label = f"{instance_label}_{m_name}"
                member_map[m_name] = {
                    'label': mem_label,
                    'type': meta.get('type', 'int'),
                    'visibility': meta.get('visibility', 'public'),
                    'offset': meta.get('offset', 0)
                }
                data_lines.append(f"{mem_label}: DW 0")

            self.symbol_table[name] = {
                'label': instance_label,
                'type': var_type,
                'is_array': False,
                'is_adt': True,
                'members': member_map
            }
            # Añadir todas las líneas de miembros a data_section
            self.data_section.extend(data_lines)
            p[0] = ("", {"type": "Declaration", "var_type": var_type, "name": name})
            return

        # Declaración de array
        if is_array_decl:
            size_expr = p[4]
            size_code = size_expr[0]
            size_ast = size_expr[2]
            base_label = self._new_label(f"arr_{name}")
            
            # Comprobar si el tamaño es un literal entero estático (optimización)
            # size_code será "MOVI R0, <int>"
            import re
            match = re.match(r"MOVI R0, (\d+)", size_code)
            
            ast_node = {"type": "ArrayDeclaration", "var_type": var_type, "name": name, "size": size_ast}

            if match:
                # Asignación estática
                size = int(match.group(1))
                self.symbol_table[name] = {
                    'label': base_label,
                    'type': var_type,
                    'is_array': True,
                    'size': size,
                    'is_adt': False,
                    'is_param': False # Array estático
                }
                words = ' '.join(['0' for _ in range(size)])
                self.data_section.append(f"{base_label}: DW {words}")
                p[0] = ("", ast_node)
            else:
                # Asignación dinámica
                self.symbol_table[name] = {
                    'label': base_label,
                    'type': var_type,
                    'is_array': True,
                    'size': None, # Desconocido en tiempo de compilación
                    'is_adt': False,
                    'is_param': True # Tratar como puntero
                }
                # Crear variable puntero
                self.data_section.append(f"{base_label}: DW 0")
                
                # Generar código de asignación
                alloc_code = f"""
                {size_code}
                MOVI R1, 8
                MUL R0, R0, R1
                LD R1, [__HEAP_PTR]
                ST R1, [{base_label}]
                ADD R1, R1, R0
                ST R1, [__HEAP_PTR]
                """
                p[0] = (alloc_code, ast_node)
        else:
            label = self._new_label(f"var_{name}")
            self.symbol_table[name] = {
                'label': label,
                'type': var_type,
                'is_array': False,
                'is_adt': False
            }
            self.data_section.append(f"{label}: DW 0")
            p[0] = ("", {"type": "Declaration", "var_type": var_type, "name": name})

    # ==========================================================================
    # 3. TIPOS DE DATOS
    # ==========================================================================
    def p_type(self, p):
        """type : INT_TYPE
                | FLOAT_TYPE
                | STRING_TYPE
                | BOOL_TYPE
                | CHAR_TYPE
                | VOID_TYPE
                | ID""" # ID para tipos TDA
        p[0] = p[1]

    # ==========================================================================
    # 4. EXPRESIONES
    # ==========================================================================
    def p_expression_binop(self, p):
        """expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression
                      | expression MOD expression
                      | expression AND expression
                      | expression OR expression
                      | expression EQ expression
                      | expression NEQ expression
                      | expression LT expression
                      | expression LE expression
                      | expression GT expression
                      | expression GE expression
                      | expression BIT_AND expression
                      | expression BIT_OR expression
                      | expression BIT_XOR expression
                      | expression SHIFT_LEFT expression
                      | expression SHIFT_RIGHT expression"""
        
        op = p[2]
        expr1 = p[1]
        expr2 = p[3]
        
        code1 = expr1[0]
        type1 = expr1[1]
        ast1 = expr1[2]
        
        code2 = expr2[0]
        type2 = expr2[1]
        ast2 = expr2[2]
        
        is_float = (type1 == 'float' or type2 == 'float')
        
        ast_node = {"type": "BinaryOp", "op": op, "left": ast1, "right": ast2}
        
        # Diccionario para operaciones aritméticas y bitwise simples
        simple_ops = {
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '%': 'MOD',
            '&': 'AND', '|': 'OR', '^': 'XOR', '<<': 'SHL', '>>': 'SHR',
            '&&': 'AND', '||': 'OR'
        }
        
        float_ops = {
            '+': 'FADD', '-': 'FSUB', '*': 'FMUL', '/': 'FDIV'
        }

        if op in simple_ops:
            if is_float and op in float_ops:
                asm_op = float_ops[op]
                p[0] = (f"{code1}\nPUSH R0\n{code2}\nPOP R1\n{asm_op} R0, R1, R0", 'float', ast_node)
            else:
                asm_op = simple_ops[op]
                p[0] = (f"{code1}\nPUSH R0\n{code2}\nPOP R1\n{asm_op} R0, R1, R0", 'int', ast_node)
            return

        # Lógica de comparación
        lbl_true = self.get_new_label()
        lbl_end = self.get_new_label()
        lbl_false = self.get_new_label() + "_false"
        
        compare_logic = "CMP R1, R0\n"
        
        # Diccionario para instrucciones de salto basadas en comparación
        # (jump_if_true, jump_if_false_check_needed)
        comparisons = {
            '==': (f"JZ {lbl_true}", False),
            '!=': (f"JNZ {lbl_true}", False),
            '<':  (f"JS {lbl_true}", False),
            '<=': (f"JS {lbl_true}\nJZ {lbl_true}", False),
            '>':  (f"JMP {lbl_true}", True), # Lógica caso especial
            '>=': (f"JMP {lbl_true}", True)  # Lógica caso especial
        }

        if op in ['>', '>=']:
             # > : No Negativo (JS->False) Y No Cero (JZ->False)
             # >=: No Negativo (JS->False)
             check_neg = f"JS {lbl_false}"
             check_zero = f"JZ {lbl_false}" if op == '>' else ""
             compare_logic += f"{check_neg}\n{check_zero}\nJMP {lbl_true}\n{lbl_false}:"
        elif op in comparisons:
             compare_logic += comparisons[op][0]

        p[0] = (f"{code1}\nPUSH R0\n{code2}\nPOP R1\n{compare_logic}\nMOVI R0, 0\nJMP {lbl_end}\n{lbl_true}:\nMOVI R0, 1\n{lbl_end}:", 'bool', ast_node)

    def p_expression_unary(self, p):
        """expression : MINUS expression
                      | NOT expression
                      | BIT_NOT expression
                      | INCREMENT expression
                      | DECREMENT expression"""
        op = p[1]
        expr = p[2]
        code = expr[0]
        type_ = expr[1]
        ast = expr[2]
        
        ast_node = {"type": "UnaryOp", "op": op, "operand": ast}
        
        if op == '-':
            # Negar: 0 - R0
            if type_ == 'float':
                p[0] = (f"{code}\nMOVI R1, 0.0\nFSUB R0, R1, R0", 'float', ast_node)
            else:
                p[0] = (f"{code}\nMOVI R1, 0\nSUB R0, R1, R0", 'int', ast_node)
        elif op == '!':
            lbl_true = self.get_new_label()
            lbl_end = self.get_new_label()
            p[0] = (f"{code}\nMOVI R1, 0\nCMP R0, R1\nJZ {lbl_true}\nMOVI R0, 0\nJMP {lbl_end}\n{lbl_true}:\nMOVI R0, 1\n{lbl_end}:", 'bool', ast_node)
        elif op == '~':
            p[0] = (f"{code}\nNOT R0, R0, R0", 'int', ast_node)
        elif op == '++':
            if type_ == 'float':
                 p[0] = (f"{code}\nMOVI R1, 1.0\nFADD R0, R0, R1", 'float', ast_node)
            else:
                 p[0] = (f"{code}\nMOVI R1, 1\nADD R0, R0, R1", 'int', ast_node)
        elif op == '--':
            if type_ == 'float':
                 p[0] = (f"{code}\nMOVI R1, 1.0\nFSUB R0, R0, R1", 'float', ast_node)
            else:
                 p[0] = (f"{code}\nMOVI R1, 1\nSUB R0, R0, R1", 'int', ast_node)

    def p_expression_group(self, p):
        """expression : LPAREN expression RPAREN"""
        p[0] = p[2]

    def p_expression_number(self, p):
        """expression : INTEGER
                      | FLOAT"""
        val = p[1]
        if isinstance(val, float):
             p[0] = (f"MOVI R0, {val}", 'float', {"type": "Literal", "value": val})
        else:
             p[0] = (f"MOVI R0, {val}", 'int', {"type": "Literal", "value": val})

    def p_expression_id(self, p):
        """expression : ID
                      | ID LBRACKET expression RBRACKET"""
        var_name = p[1]
        is_array_access = len(p) == 5
        
        entry = self.symbol_table.get(var_name, {})
        var_type = entry.get('type', 'int')

        if is_array_access:
            index_expr = p[3]
            index_code = index_expr[0]
            index_ast = index_expr[2]
            p[0] = (self._generate_array_access(var_name, index_code, p), var_type, {"type": "ArrayAccess", "array": var_name, "index": index_ast})
        else:
            p[0] = (self._generate_var_access(var_name, p), var_type, {"type": "Identifier", "name": var_name})

    def p_expression_member(self, p):
        """expression : ID DOT ID"""
        obj = p[1]
        member = p[3]
        
        if obj not in self.symbol_table:
            self._error(f"Instancia TDA '{obj}' no declarada", p)
            p[0] = ("MOVI R0, 0", 'int', {"type": "Literal", "value": 0})
            return
            
        inst = self.symbol_table[obj]
        if not (isinstance(inst, dict) and inst.get('is_adt')):
            self._error(f"'{obj}' no es una instancia TDA", p)
            p[0] = ("MOVI R0, 0", 'int', {"type": "Literal", "value": 0})
            return
            
        members = inst.get('members', {})
        if member not in members:
            self._error(f"Miembro '{member}' no encontrado en instancia TDA '{obj}'", p)
            p[0] = ("MOVI R0, 0", 'int', {"type": "Literal", "value": 0})
            return
            
        meta = members[member]
        if meta.get('visibility') == 'private' and self.current_context is None:
            self._error(f"Acceso ilegal a miembro privado '{member}' de '{obj}'", p)
            p[0] = ("MOVI R0, 0", 'int', {"type": "Literal", "value": 0})
            return
            
        p[0] = (f"LD R0, [{meta['label']}]", meta.get('type', 'int'), {"type": "MemberAccess", "object": obj, "member": member})

    def p_expression_func_call(self, p):
        """expression : func_call"""
        # func_call devuelve cadena de código. Necesitamos inferir el tipo.
        # Por ahora, asumir 'int' a menos que rastreemos tipos de retorno de funciones.
        # TODO: Rastrear tipos de retorno de funciones en tabla de símbolos.
        p[0] = (p[1][0], 'int', p[1][1])

    def p_expression_string(self, p):
        """expression : STRING"""
        # Generar etiqueta única para cadena en sección de datos
        self.string_count += 1
        str_label = f"STR_{self.string_count}"
        
        # Añadir cadena a sección de datos usando directiva DB
        # Escapar la cadena apropiadamente y añadir terminador nulo
        string_content = p[1]
        self.data_section.append(f'{str_label}: DB "{string_content}", 0')
        
        # Devolver código para cargar dirección de cadena en R0
        p[0] = (f"MOVI R0, {str_label}", 'string', {"type": "Literal", "value": string_content})

    def p_expression_bool(self, p):
        """expression : TRUE
                      | FALSE"""
        val = True if p[1] == 'true' else False
        p[0] = ("MOVI R0, 1" if val else "MOVI R0, 0", 'bool', {"type": "Literal", "value": val})

    # Lista de parámetros (restaurar reglas perdidas)
    def p_param_list_opt(self, p):
        """param_list_opt : param_list
                           | empty"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = []

    def p_param_list(self, p):
        """param_list : param COMMA param_list
                       | param"""
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    def p_param(self, p):
        """param : type ID
                  | type ID LBRACKET RBRACKET"""
        if len(p) == 3:
            p[0] = (p[1], p[2])
        else:
            # Parámetro array: marcar como tupla para que p_func_decl sepa que es array
            p[0] = (p[1], (p[2], 'array'))

    def p_return_stmt(self, p):
        """return_stmt : RETURN expression SEMI
                       | RETURN SEMI"""
        if len(p) == 4:
            expr = p[2]
            expr_code = expr[0]
            expr_ast = expr[2]
            p[0] = (f"{expr_code}\nRET", {"type": "Return", "value": expr_ast}) # Resultado en R0
        else:
            p[0] = ("RET", {"type": "Return", "value": None})

    def p_func_call_stmt(self, p):
        """func_call_stmt : func_call SEMI"""
        p[0] = p[1]

    def p_func_call(self, p):
        """func_call : ID LPAREN arg_list_opt RPAREN
                     | ID DOT ID LPAREN arg_list_opt RPAREN"""
        
        if len(p) == 5:
            # Llamada a función normal
            func_name = p[1]
            args = p[3] if p[3] else []
            
            ast_node = {"type": "Call", "function": func_name, "args": [arg[2] for arg in args]}

            # Función especial incorporada 'print' para imprimir sin nueva línea
            if func_name == 'print':
                if not args:
                    p[0] = ("", ast_node)
                    return
                
                # Solo soportar 1 argumento por ahora
                arg_code, arg_type, arg_ast = args[0]
                
                # Si es una cadena
                if arg_type == 'string':
                     p[0] = (f"{arg_code}\nOUTS R0, 0xFFFF0008", ast_node)
                elif arg_type == 'float':
                     # Float sin nueva línea: func=6 (subop=3)
                     p[0] = (f"{arg_code}\nOUT R0, 0xFFFF0008, 6", ast_node)
                else:
                     # Int sin nueva línea: func=4 (subop=2)
                     p[0] = (f"{arg_code}\nOUT R0, 0xFFFF0008, 4", ast_node)
                return

            # Construir código de empuje de argumentos - empujar en orden inverso para que el primer arg esté arriba
            args_code = ""
            if args:
                for arg_code, arg_type, arg_ast in reversed(args):
                    # Asegurar que arg_code termina con nueva línea
                    if not arg_code.endswith('\n'):
                        arg_code += '\n'
                    args_code += f"{arg_code}PUSH R0\n"
            
            # Registrar llamada para validación posterior
            self.called_functions.add(func_name)
            
            p[0] = (f"{args_code}CALL FUNC_{func_name}", ast_node)
            
        else:
            # Llamada a método: obj.method(args)
            obj_name = p[1]
            method_name = p[3]
            args = p[5] if p[5] else []
            
            ast_node = {"type": "MethodCall", "object": obj_name, "method": method_name, "args": [arg[2] for arg in args]}
            
            if obj_name not in self.symbol_table:
                self._error(f"Objeto '{obj_name}' no declarado", p)
                p[0] = ("", ast_node)
                return
            
            obj_entry = self.symbol_table[obj_name]
            if not obj_entry.get('is_adt'):
                self._error(f"'{obj_name}' no es una instancia TDA", p)
                p[0] = ("", ast_node)
                return
            
            adt_type = obj_entry['type']
            adt_info = self.type_table.get(adt_type)
            
            if not adt_info:
                self._error(f"Tipo TDA desconocido '{adt_type}'", p)
                p[0] = ("", ast_node)
                return
            
            methods = adt_info.get('methods', {})
            if method_name not in methods:
                self._error(f"Método '{method_name}' no encontrado en TDA '{adt_type}'", p)
                p[0] = ("", ast_node)
                return
            
            method_info = methods[method_name]
            
            # Comprobar visibilidad
            if method_info['visibility'] == 'private':
                # Permitir si dentro del mismo contexto TDA
                if self.current_context != adt_type:
                    self._error(f"Acceso ilegal a método privado '{method_name}' de '{adt_type}'", p)
                    p[0] = ("", ast_node)
                    return
            
            # Preparar argumentos
            # Empujar args en orden inverso
            args_code = ""
            if args:
                for arg_code, arg_type, arg_ast in reversed(args):
                    if not arg_code.endswith('\n'):
                        arg_code += '\n'
                    args_code += f"{arg_code}PUSH R0\n"
            
            # Empujar 'this' (dirección del objeto)
            obj_label = obj_entry['label']
            this_code = f"MOVI R0, {obj_label}\nPUSH R0\n"
            
            mangled_label = method_info['label']
            p[0] = (f"{args_code}{this_code}CALL {mangled_label}", ast_node)

    # ==========================================================================
    # 6. FUNCIONES
    # ==========================================================================
    def p_func_decl(self, p):
        """func_decl : func_start statements ENDFUNC"""
        func_name, params, param_setup, param_names, original_name = p[1]
        body_code, body_ast = p[2]
        
        # Asegurar que el cuerpo de la función no se mezcle con el código principal
        # Marcamos el inicio y fin claramente para el separador en p_program
        result = f"FUNC_{func_name}:\n{param_setup}{body_code}\nRET"
        
        # Eliminar parámetros de la tabla de símbolos (fin del ámbito de función)
        for pname in param_names:
            if pname in self.symbol_table:
                del self.symbol_table[pname]
        
        ast_node = {"type": "FunctionDecl", "name": original_name, "params": params, "body": body_ast}
        p[0] = (result, ast_node)
    
    def p_func_start(self, p):
        """func_start : FUNC ID LPAREN param_list_opt RPAREN COLON"""
        func_name = p[2]
        original_name = func_name
        params = p[4] if p[4] else []
        
        if self.current_context:
            # Nombre decorado (mangled)
            mangled_name = f"{self.current_context}_{func_name}"
            
            # Almacenar info del método
            self.current_adt_methods[func_name] = {
                'label': f"FUNC_{mangled_name}",
                'params': params.copy(), # Params originales antes de añadir 'this'
                'visibility': 'public' # Por defecto
            }
            
            # Añadir param 'this'
            # (type, name)
            params.insert(0, (self.current_context, 'this'))
            func_name = mangled_name
        
        # Añadir parámetros a la tabla de símbolos AHORA (antes de que se parsen las sentencias)
        # Después de CALL, la pila tiene: [ret_addr] [arg1] [arg2] ...
        # El primer POP obtiene ret_addr (manejado por RET), así que necesitamos saltarlo
        param_setup = ""
        param_names = []
        
        # Primero, sacar y guardar la dirección de retorno temporalmente
        param_setup += "POP R14\n"  # R14 = dirección de retorno
        
        # Ahora sacar parámetros en orden normal (el primer param está arriba)
        for param_type, param_name in params:
            is_array = False
            if isinstance(param_name, tuple):  # Parámetro array
                param_name = param_name[0]
                is_array = True
            
            param_names.append(param_name)
            label = self._new_label(f"param_{param_name}")
            self.symbol_table[param_name] = {
                'label': label,
                'type': param_type,
                'is_array': is_array,
                'is_adt': False,
                'is_param': True  # Marcar como parámetro
            }
            self.data_section.append(f"{label}: DW 0")
            # Sacar parámetro de la pila al almacenamiento
            param_setup += f"POP R0\nST R0, [{label}]\n"
        
        # Empujar dirección de retorno de vuelta para instrucción RET
        param_setup += "PUSH R14\n"
        
        # Registrar símbolo de función
        self.symbol_table[f"FUNC_{func_name}"] = {
            'type': 'function',
            'label': f"FUNC_{func_name}",
            'is_array': False,
            'is_adt': False,
            'params': params
        }
        
        p[0] = (func_name, params, param_setup, param_names, original_name)

    def p_arg_list_opt(self, p):
        """arg_list_opt : arg_list
                        | empty"""
        p[0] = p[1] if len(p) == 2 and p[1] is not None else []

    def p_arg_list(self, p):
        """arg_list : arg COMMA arg_list
                    | arg"""
        if len(p) == 4:
            # Mantener orden izquierda-derecha
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]
    
    def p_arg(self, p):
        """arg : ID
              | expression"""
        # Siempre usar el resultado de la expresión (que maneja búsqueda de ID vía _generate_var_access)
        expr = p[1]
        expr_code = expr[0]
        expr_type = expr[1]
        expr_ast = expr[2]
        p[0] = (expr_code, expr_type, expr_ast)

    # ==========================================================================
    # 7. TIPOS DE DATOS ABSTRACTOS (TDAs)
    # ==========================================================================
    def p_adt_head(self, p):
        """adt_head : ADT ID LPAREN param_list_opt RPAREN COLON"""
        self.current_context = p[2]
        self.current_adt_members = {}
        self.current_adt_methods = {}
        self.current_adt_offset = 0
        p[0] = p[2]

    def p_adt_decl(self, p):
        """adt_decl : adt_head adt_body ENDADT"""
        adt_name = p[1]
        # raw_members contiene variables y métodos
        raw_members = [m for m in p[2] if m is not None]
        
        members_dict = {}
        method_code_list = []
        methods_ast = []
        members_ast = []
        
        for item in raw_members:
            name = item[0]
            if len(item) >= 2 and item[1] == 'method':
                # ('method', name, code, visibility, ast)
                method_code_list.append(item[2])
                methods_ast.append(item[4])
            else:
                # Variable (name, type, visibility)
                mtype = item[1]
                vis = item[2]
                if name in self.current_adt_members:
                    offset = self.current_adt_members[name]['offset']
                    members_dict[name] = {
                        'visibility': vis,
                        'type': mtype,
                        'offset': offset
                    }
                members_ast.append({"name": name, "type": mtype, "visibility": vis})
        
        self.type_table[adt_name] = {
            'members': members_dict,
            'methods': self.current_adt_methods,
            'size': len(members_dict)
        }
        self.current_context = None
        self.current_adt_members = {}
        self.current_adt_methods = {}
        self.current_adt_offset = 0
        
        ast_node = {"type": "ADTDecl", "name": adt_name, "members": members_ast, "methods": methods_ast}
        # Devolver el código de método acumulado
        p[0] = ("\n".join(method_code_list), ast_node)

    def p_adt_body(self, p):
        """adt_body : visibility_block adt_body
                    | visibility_block"""
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

    def p_visibility_block(self, p):
        """visibility_block : PRIVATE COLON member_list
                            | PUBLIC COLON member_list"""
        visibility = p[1].lower()
        annotated = []
        for item in p[3]:
            if item is not None:
                if item[0] == 'method':
                    # item is ('method', name, code, ast)
                    name = item[1]
                    code = item[2]
                    ast = item[3]
                    # Actualizar visibilidad en current_adt_methods
                    if name in self.current_adt_methods:
                        self.current_adt_methods[name]['visibility'] = visibility
                    
                    annotated.append(('method', name, code, visibility, ast))
                else:
                    name, mtype = item
                    annotated.append((name, mtype, visibility))
        p[0] = annotated

    def p_member_list(self, p):
        """member_list : member_decl member_list
                       | member_decl"""
        if len(p) == 3:
            p[0] = ([p[1]] if p[1] else []) + p[2]
        else:
            p[0] = [p[1]] if p[1] else []

    def p_member_decl(self, p):
        """member_decl : type ID SEMI
                       | func_decl"""
        if len(p) == 4:
            name = p[2]
            mtype = p[1]
            # Añadir a miembros TDA actuales
            if self.current_context:
                self.current_adt_members[name] = {
                    'type': mtype,
                    'offset': self.current_adt_offset
                }
                self.current_adt_offset += 1
            p[0] = (name, mtype)  # (name,type)
        else:
            # p[1] es (code, ast)
            code = p[1][0]
            ast = p[1][1]
            name = ast['name']
            p[0] = ('method', name, code, ast)

    # ----------------------------------------
    # Asignaciones
    # ----------------------------------------
    def p_assignment(self, p):
        """assignment : lvalue ASSIGN expression SEMI"""
        target = p[1]
        expr = p[3]
        expr_code = expr[0]
        expr_ast = expr[2]
        
        kind = target[0]
        
        if kind == 'array':
            # target: ('array', arr_name, index_code, index_ast, lvalue_ast)
            arr_name = target[1]
            index_code = target[2]
            index_ast = target[3]
            
            code = self._generate_array_assignment(arr_name, index_code, expr_code, p)
            ast = {"type": "ArrayAssignment", "target": arr_name, "index": index_ast, "value": expr_ast}
            p[0] = (code, ast)
            
        elif kind == 'member':
            # target: ('member', obj_name, member_name, lvalue_ast)
            obj_name = target[1]
            member_name = target[2]
            
            code = self._generate_member_assignment(obj_name, member_name, expr_code, p)
            ast = {"type": "MemberAssignment", "object": obj_name, "member": member_name, "value": expr_ast}
            p[0] = (code, ast)
            
        elif kind == 'var':
            # target: ('var', name, lvalue_ast)
            name = target[1]
            
            code = self._generate_var_assignment(name, expr_code, p)
            ast = {"type": "Assignment", "target": name, "value": expr_ast}
            p[0] = (code, ast)
            
        else:
            self._error("Objetivo de asignación inválido", p)
            p[0] = ("", None)

    def p_lvalue(self, p):
        """lvalue : ID
                  | ID DOT ID
                  | ID LBRACKET expression RBRACKET"""
        if len(p) == 2:
            # ID
            p[0] = ('var', p[1], {"type": "Identifier", "name": p[1]})
        elif len(p) == 4 and p[2] == '.':
            # ID.ID
            obj_name = p[1]
            member_name = p[3]
            p[0] = ('member', obj_name, member_name, {"type": "MemberAccess", "object": obj_name, "member": member_name})
        elif len(p) == 5:
            # ID[expr]
            arr_name = p[1]
            index_expr = p[3]
            # index_expr is (code, type, ast)
            index_code = index_expr[0]
            index_ast = index_expr[2]
            p[0] = ('array', arr_name, index_code, index_ast, {"type": "ArrayAccess", "array": arr_name, "index": index_ast})

    # ----------------------------------------
    # Flujo de Control (Extendido)
    # ----------------------------------------
    def p_for_stmt(self, p):
        """for_stmt : for_header statements ENDFOR"""
        init_code, check_code, inc_code, lbl_start, lbl_end, var_name, start_ast, end_ast = p[1]
        body = p[2]
        body_code = body[0]
        body_ast = body[1]
        
        code = f"{init_code}\n{lbl_start}:\n{check_code}\n{body_code}\n{inc_code}\nJMP {lbl_start}\n{lbl_end}:"
        ast = {"type": "For", "variable": var_name, "start": start_ast, "end": end_ast, "body": body_ast}
        p[0] = (code, ast)
        self.loop_stack.pop()

    def p_for_header(self, p):
        """for_header : FOR LPAREN ID IN expression RANGE expression RPAREN COLON"""
        var_name = p[3]
        start_expr = p[5]
        start_code = start_expr[0]
        start_ast = start_expr[2]
        
        end_expr = p[7]
        end_code = end_expr[0]
        end_ast = end_expr[2]
        
        if var_name not in self.symbol_table:
            self.symbol_table[var_name] = var_name
            self.data_section.append(f"{var_name}: DW 0")
        
        lbl_start = self.get_new_label()
        lbl_end = self.get_new_label()
        self.loop_stack.append((lbl_start, lbl_end))
        
        init_code = f"{start_code}\nST R0, [{var_name}]"
        check_code = f"{end_code}\nPUSH R0\nLD R0, [{var_name}]\nPOP R1\nCMP R0, R1\nJS {lbl_start}_cont\nJMP {lbl_end}\n{lbl_start}_cont:"
        inc_code = f"LD R0, [{var_name}]\nMOVI R1, 1\nADD R0, R0, R1\nST R0, [{var_name}]"
        
        p[0] = (init_code, check_code, inc_code, lbl_start, lbl_end, var_name, start_ast, end_ast)

    def p_break_stmt(self, p):
        """break_stmt : BREAK SEMI"""
        ast = {"type": "Break"}
        if self.loop_stack:
            _, lbl_end = self.loop_stack[-1]
            p[0] = (f"JMP {lbl_end}", ast)
        else:
            print("Error: break fuera de bucle")
            p[0] = ("", ast)

    def p_continue_stmt(self, p):
        """continue_stmt : CONTINUE SEMI"""
        ast = {"type": "Continue"}
        if self.loop_stack:
            lbl_start, _ = self.loop_stack[-1]
            p[0] = (f"JMP {lbl_start}", ast)
        else:
            print("Error: continue fuera de bucle")
            p[0] = ("", ast)

    # ----------------------------------------
    # Flujo de Control (Básico)
    # ----------------------------------------
    def p_if_stmt(self, p):
        """if_stmt : IF LPAREN expression RPAREN COLON statements ENDIF
                   | IF LPAREN expression RPAREN COLON statements ELSE COLON statements ENDIF"""
        
        cond = p[3]
        cond_code = cond[0]
        cond_ast = cond[2]
        
        true_block = p[6]
        true_code = true_block[0]
        true_ast = true_block[1]
        
        lbl_else = self.get_new_label()
        lbl_end = self.get_new_label()
        
        if len(p) == 8: # Sin else
            code = f"{cond_code}\nMOVI R1, 0\nCMP R0, R1\nJZ {lbl_end}\n{true_code}\n{lbl_end}:"
            ast = {"type": "If", "condition": cond_ast, "then": true_ast, "else": None}
            p[0] = (code, ast)
        else: # Con else
            else_block = p[9]
            else_code = else_block[0]
            else_ast = else_block[1]
            
            code = f"{cond_code}\nMOVI R1, 0\nCMP R0, R1\nJZ {lbl_else}\n{true_code}\nJMP {lbl_end}\n{lbl_else}:\n{else_code}\n{lbl_end}:"
            ast = {"type": "If", "condition": cond_ast, "then": true_ast, "else": else_ast}
            p[0] = (code, ast)

    def p_while_stmt(self, p):
        """while_stmt : WHILE LPAREN expression RPAREN COLON statements ENDWHILE"""
        cond = p[3]
        cond_code = cond[0]
        cond_ast = cond[2]
        
        body = p[6]
        body_code = body[0]
        body_ast = body[1]
        
        lbl_start = self.get_new_label()
        lbl_end = self.get_new_label()
        self.loop_stack.append((lbl_start, lbl_end))
        
        code = f"{lbl_start}:\n{cond_code}\nMOVI R1, 0\nCMP R0, R1\nJZ {lbl_end}\n{body_code}\nJMP {lbl_start}\n{lbl_end}:"
        ast = {"type": "While", "condition": cond_ast, "body": body_ast}
        p[0] = (code, ast)
        self.loop_stack.pop()

    def p_output_stmt(self, p):
        """output_stmt : OUTPUT expression SEMI"""
        expr = p[2]
        expr_code = expr[0]
        expr_type = expr[1]
        expr_ast = expr[2]
        
        ast = {"type": "Output", "value": expr_ast}
        
        if expr_type == 'string':
            # Usar OUTS para salida de cadena
            p[0] = (f"{expr_code}\nOUTS R0, 0xFFFF0008", ast)
        elif expr_type == 'float':
             # Usar OUT con func=6 (subop=3 -> print float)
             # 6 = (3 << 1) | 0
             p[0] = (f"{expr_code}\nOUT R0, 0xFFFF0008, 6", ast)
        else:
            # Usar OUT para salida numérica
            p[0] = (f"{expr_code}\nOUT R0, 0xFFFF0008", ast)

    def p_print_stmt(self, p):
        """statement : ID LPAREN expression RPAREN SEMI"""
        # Comprobar sintaxis "print(expr)" para imprimir sin nueva línea
        if p[1] == 'print':
            expr = p[3]
            expr_code = expr[0]
            expr_type = expr[1]
            expr_ast = expr[2]
            
            ast = {"type": "Call", "function": "print", "args": [expr_ast]}
            
            if expr_type == 'float':
                 # Usar OUT con func=6 (subop=3 -> print float)
                 p[0] = (f"{expr_code}\nOUT R0, 0xFFFF0008, 6", ast)
            else:
                 # Usar OUT con func=4 (subop=2 -> print int sin nueva línea)
                 # 4 = (2 << 1) | 0
                 p[0] = (f"{expr_code}\nOUT R0, 0xFFFF0008, 4", ast)
        else:
            # Retroceder a lógica de llamada a función normal si no es 'print'
            # Pero espera, p_statement ya maneja func_call_stmt.
            # Esta regla podría entrar en conflicto.
            # Mejor añadir 'print' como palabra clave o manejarlo en func_call.
            p[0] = ("", None)
            
    # Manejaremos 'print' como una llamada a función especial en p_func_call


    def p_input_stmt(self, p):
        """input_stmt : INPUT ID SEMI"""
        var_name = p[2]
        ast = {"type": "Input", "variable": var_name}
        
        if var_name not in self.symbol_table:
             print(f"Error: Variable {var_name} no declarada.")
             p[0] = ("", ast)
             return
        entry = self.symbol_table[var_name]
        label = entry['label'] if isinstance(entry, dict) and 'label' in entry else var_name
        p[0] = (f"IN R0, 0xFFFF0018\nST R0, [{label}]", ast)

    def p_empty(self, p):
        """empty :"""
        pass

    def p_error(self, p):
        self.error_count += 1
        if p:
            print(f"Error de sintaxis en '{p.value}' línea {p.lineno}")
        else:
            print("Error de sintaxis en EOF")

    def parse(self, code, lexer):
        self.asm = ""
        self.label_count = 0
        self.string_count = 0
        self.symbol_table = {}
        self.data_section = []
        self.error_count = 0
        self.called_functions = set()
        result = self.parser.parse(code, lexer=lexer)
        
        # Validar llamadas a funciones
        for func_name in self.called_functions:
            func_label = f"FUNC_{func_name}"
            is_defined = func_label in self.symbol_table
            is_library = func_label in self.library_functions
            
            if not is_defined and not is_library:
                print(f"[Error del Parser] Función '{func_name}' llamada pero no definida ni encontrada en librerías.")
                self.error_count += 1

        if self.error_count > 0:
            return None
        return result

    # ----------------------------------------
    # Métodos Auxiliares de Generación
    # ----------------------------------------
    def _generate_array_access(self, var_name, index_code, p):
        if var_name not in self.symbol_table:
            self._error(f"Array '{var_name}' no declarado", p)
            return "MOVI R0, 0"
            
        entry = self.symbol_table[var_name]
        if not (isinstance(entry, dict) and entry.get('is_array')):
            self._error(f"'{var_name}' no es un array", p)
            return "MOVI R0, 0"
            
        base_label = entry['label']
        # Cálculo de dirección común: index * 8
        calc_offset = f"{index_code}\nMOVI R1, 8\nMUL R1, R0, R1"
        
        if entry.get('is_param'):
            # Dirección base es dinámica (pasada como param)
            # Cargar el valor de dirección almacenado en la ubicación del parámetro
            return f"{calc_offset}\nLD R2, [{base_label}]\nADD R15, R2, R1\nLD R0, R15, 0"
        
        # Dirección base es etiqueta estática
        return f"{calc_offset}\nMOVI R2, {base_label}\nADD R15, R2, R1\nLD R0, R15, 0"

    def _generate_var_access(self, var_name, p):
        # Comprobar acceso a miembro TDA vía 'this' implícito
        if self.current_context and var_name in self.current_adt_members:
            offset = self.current_adt_members[var_name]['offset']
            this_entry = self.symbol_table.get('this')
            if this_entry:
                this_label = this_entry['label']
                byte_offset = offset * 8
                # Cargar puntero 'this' luego cargar miembro en offset
                return f"LD R1, [{this_label}]\nLD R0, R1, {byte_offset}"

        if var_name not in self.symbol_table:
            print(f"Error: Variable {var_name} no declarada.")
            return "MOVI R0, 0"

        entry = self.symbol_table[var_name]
        
        # Si es array, devolver dirección
        if isinstance(entry, dict) and entry.get('is_array'):
            label = entry['label']
            if entry.get('is_param'):
                return f"LD R0, [{label}]"
            else:
                return f"MOVI R0, {label}"

        # Marcador de valor de instancia TDA
        if isinstance(entry, dict) and entry.get('is_adt'):
            # Devolver la dirección base de la instancia
            label = entry.get('label', var_name)
            return f"MOVI R0, {label}"
        
        label = entry.get('label', var_name)
        return f"LD R0, [{label}]"

    def _generate_var_assignment(self, target, expr_code, p):
        # Comprobar asignación a miembro TDA vía 'this' implícito
        if self.current_context and target in self.current_adt_members:
            offset = self.current_adt_members[target]['offset']
            this_entry = self.symbol_table.get('this')
            if this_entry:
                this_label = this_entry['label']
                byte_offset = offset * 8
                # Almacenar R0 en [this + offset]
                return f"{expr_code}\nLD R1, [{this_label}]\nST R0, R1, {byte_offset}"

        if target not in self.symbol_table:
            self._error(f"Variable '{target}' no declarada", p)
            return ""
            
        entry = self.symbol_table[target]
        label = entry.get('label', target)
        return f"{expr_code}\nST R0, [{label}]"

    def _generate_array_assignment(self, arr_name, index_code, expr_code, p):
        if arr_name not in self.symbol_table:
            self._error(f"Array '{arr_name}' no declarado", p)
            return ""
            
        entry = self.symbol_table[arr_name]
        if not entry.get('is_array'):
            self._error(f"'{arr_name}' no es un array", p)
            return ""
            
        base_label = entry['label']
        calc_offset = f"{index_code}\nMOVI R1, 8\nMUL R1, R0, R1"
        
        # Calcular dirección objetivo en R15
        if entry.get('is_param'):
            addr_calc = f"{calc_offset}\nLD R2, [{base_label}]\nADD R15, R2, R1"
        else:
            addr_calc = f"{calc_offset}\nMOVI R2, {base_label}\nADD R15, R2, R1"
            
        return f"{addr_calc}\nPUSH R15\n{expr_code}\nPOP R15\nST R0, R15, 0"

    def _generate_member_assignment(self, obj, member, expr_code, p):
        inst = self.symbol_table.get(obj)
        if not inst or not inst.get('is_adt'):
            self._error(f"'{obj}' no es una instancia TDA", p)
            return ""
            
        meta = inst['members'].get(member)
        if not meta:
            self._error(f"Miembro '{member}' no encontrado en '{obj}'", p)
            return ""
            
        if meta.get('visibility') == 'private' and self.current_context is None:
            self._error(f"Escritura ilegal a miembro privado '{member}' de '{obj}'", p)
            return ""
            
        return f"{expr_code}\nST R0, {meta['label']}"


