import sys
import os

# Anadir directorio src al path para permitir 'import ply.yacc'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import ply.yacc as yacc

class Parser:
    """
    El Parser se encarga del analisis sintactico y la generacion de codigo ensamblador.
    Utiliza la libreria PLY (Python Lex-Yacc) para procesar los tokens.
    
    Estrategia de Generacion de Codigo:
    - El codigo se genera en una sola pasada (Single-pass compiler).
    - Las expresiones se evaluan utilizando una estrategia basada en Pila (Stack Machine):
      se empujan operandos y los operadores consumen de la pila.
    - Las estructuras de control (if, while, for) generan etiquetas y saltos (JMP, JZ, etc.).
    """
    def __init__(self, tokens, library_functions=None):
        self.tokens = tokens
        self.parser = yacc.yacc(module=self)
        self.library_functions = library_functions if library_functions else set()
        self.called_functions = set()

        # Tabla de Simbolos: Estructura central para el analisis semantico.
        # Ahora implementada como una pila de ambitos (scopes) para manejar variables locales.
        # self.scopes[0] es el ambito global.
        self.scopes = [{}]

        # Seccion de Datos: Almacena las directivas de memoria (DW, DB) que se
        # emitiran al final del codigo ensamblador (despues del HALT).
        self.data_section = []

        # Contador de etiquetas para etiquetas unicas
        self.label_count = 0
        
        # Contador de cadenas para etiquetas de seccion de datos
        self.string_count = 0

        # Tabla de Tipos TDA: {
        #   'NombreTDA': {
        #       'members': { 'nombreMiembro': {'visibility': 'public'|'private', 'offset': int} },
        #       'operations': { 'nombreOp': {'visibility': vis, 'params': [...], 'body': <asm o alto-nivel>} },
        #       'size': <conteo_miembros>
        #   }
        # }
        self.type_table = {}

        # Contexto actual: None o nombre de TDA mientras se parsea una operacion TDA
        self.current_context = None
        self.current_adt_members = {}
        self.current_adt_offset = 0

        # Pila de bucles para break/continue
        self.loop_stack = []

        # Ensamblador acumulado para un parseo
        self.asm = ""
        
        # Contador de errores
        self.error_count = 0

    # Metodos de gestion de Scope (Ambito)
    def _enter_scope(self):
        self.scopes.append({})

    def _exit_scope(self):
        self.scopes.pop()

    def _lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _declare(self, name, info, p):
        if name in self.scopes[-1]:
            self._error(f"Identificador '{name}' ya declarado en este ambito", p)
        self.scopes[-1][name] = info

    # Generador de etiquetas de utilidad usado por la nueva logica de declaracion
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
        # Esta regla define la estructura final del ejecutable.
        # 1. Inicializa el puntero al Heap (__HEAP_PTR).
        # 2. Separa el codigo de funciones del codigo principal (Main).
        # 3. Genera el punto de entrada (ORG 0) y el salto al Main.
        
        code, ast = p[1]
        
        # Anadir Puntero al Heap
        self.data_section.append("__HEAP_PTR: DW __HEAP_START")
        # __HEAP_START se anade al final del archivo en el pipeline para evitar sobrescritura por librerias
        
        data_section_str = "\n".join(self.data_section)
        
        # Si no hay funciones definidas, todo es codigo principal
        if 'FUNC_' not in code:
             p[0] = (f"ORG 0\n{code}\nHALT\n\n{data_section_str}", {"type": "Program", "body": ast})
             return

        # Separar funciones del codigo principal
        lines = code.split('\n')
        functions = []
        main_code = []
        in_function = False
        
        for line in lines:
            stripped = line.strip()
            # Detectar inicio de funcion
            if stripped.startswith('FUNC_'):
                in_function = True
            
            if in_function:
                # Detectar fin de funcion (__END_FUNC__)
                if stripped == '__END_FUNC__':
                    functions.append('RET')
                    in_function = False
                else:
                    functions.append(line)
            elif stripped: # Lineas que no son funciones ni vacias van al main
                main_code.append(line)
        
        func_section = "\n".join(functions)
        main_section = "\n".join(main_code)
        
        # Invocar automaticamente a main() si existe
        if self._lookup("FUNC_main"):
            main_section += "\nCALL FUNC_main"

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
        # Maneja la reserva de memoria para variables.
        # - Variables simples: Se crea una etiqueta y se reserva espacio con DW 0.
        # - Arrays estaticos: Se reserva un bloque contiguo de memoria.
        # - Arrays dinamicos: Se genera codigo para solicitar memoria al Heap en tiempo de ejecucion.
        
        var_type = p[1]
        name = p[2]
        is_init = len(p) == 6 and p[3] == '='
        is_array_decl = len(p) == 7 and p[3] == '['

        # Declaracion con inicializacion
        if is_init:
            expr = p[4]
            expr_code = expr[0]
            expr_type = expr[1]
            expr_ast = expr[2]

            # Validacion de Tipos
            if var_type != expr_type:
                self._error(f"Error de tipo: No se puede asignar '{expr_type}' a variable de tipo '{var_type}'", p)

            label = self._new_label(f"var_{name}")
            self._declare(name, {
                'label': label,
                'type': var_type,
                'is_array': False,
                'is_adt': False
            }, p)
            self.data_section.append(f"{label}: DW 0")
            
            p[0] = (f"{expr_code}\nST R0, [{label}]", {"type": "Declaration", "var_type": var_type, "name": name, "init": expr_ast})
            return

        # Declaracion de array (DEBE IR ANTES que la verificacion de TDA simple)
        if is_array_decl:
            size_expr = p[4]
            size_code = size_expr[0]
            size_ast = size_expr[2]
            base_label = self._new_label(f"arr_{name}")
            
            # Comprobar si el tamano es un literal entero estatico (optimizacion)
            # size_code sera "MOVI R0, <int>"
            import re
            match = re.match(r"MOVI R0, (\d+)", size_code)
            
            ast_node = {"type": "ArrayDeclaration", "var_type": var_type, "name": name, "size": size_ast}

            # Verificar si es un array de TDAs
            if var_type in self.type_table:
                # Array de TDA
                adt_info = self.type_table[var_type]
                element_size = adt_info['size']  # Número de miembros en el TDA
                
                if match:
                    # Array estático de TDAs
                    array_size = int(match.group(1))
                    
                    # Crear estructura completa: etiquetas para cada miembro de cada elemento
                    self.data_section.append(f"{base_label}:")
                    
                    for i in range(array_size):
                        elem_label = f"{base_label}_{i}"
                        self.data_section.append(f"{elem_label}:")
                        
                        for member_name, member_info in adt_info['members'].items():
                            member_label = f"{elem_label}_{member_name}"
                            self.data_section.append(f"{member_label}: DW 0")
                    
                    self._declare(name, {
                        'label': base_label,
                        'type': var_type,
                        'is_array': True,
                        'size': array_size,
                        'element_size': element_size,
                        'is_adt_array': True,
                        'is_param': False,
                        'adt_info': adt_info
                    }, p)
                    p[0] = ("", ast_node)
                else:
                    # Array dinámico de TDAs
                    total_element_size = element_size * 8  # Cada miembro = 8 bytes
                    
                    alloc_code = f"""
                {size_code}
                MOVI R1, {total_element_size}
                MUL R0, R0, R1
                LD R1, [__HEAP_PTR]
                ST R1, [{base_label}]
                ADD R1, R1, R0
                ST R1, [__HEAP_PTR]
                """
                    
                    self._declare(name, {
                        'label': base_label,
                        'type': var_type,
                        'is_array': True,
                        'size': None,
                        'element_size': element_size,
                        'is_adt_array': True,
                        'is_param': True,
                        'adt_info': adt_info
                    }, p)
                    self.data_section.append(f"{base_label}: DW 0")
                    p[0] = (alloc_code, ast_node)
            else:
                # Array de tipo primitivo (código original)
                if match:
                    # Asignacion estatica
                    size = int(match.group(1))
                    self._declare(name, {
                        'label': base_label,
                        'type': var_type,
                        'is_array': True,
                        'size': size,
                        'is_adt': False,
                        'is_param': False # Array estatico
                    }, p)
                    words = ' '.join(['0' for _ in range(size)])
                    self.data_section.append(f"{base_label}: DW {words}")
                    p[0] = ("", ast_node)
                else:
                    # Asignacion dinámica
                    self._declare(name, {
                        'label': base_label,
                        'type': var_type,
                        'is_array': True,
                        'size': None, # Desconocido en tiempo de compilación
                        'is_adt': False,
                        'is_param': True # Tratar como puntero
                    }, p)
                    # Crear variable puntero
                    self.data_section.append(f"{base_label}: DW 0")
                    
                    # Generar codigo de asignacion
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
            return

        # Declaracion de instancia TDA (el tipo existe en type_table)
        # IMPORTANTE: Esto va DESPUÉS de verificar arrays
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

            self._declare(name, {
                'label': instance_label,
                'type': var_type,
                'is_array': False,
                'is_adt': True,
                'members': member_map
            }, p)
            # Anadir todas las lineas de miembros a data_section
            self.data_section.extend(data_lines)
            p[0] = ("", {"type": "Declaration", "var_type": var_type, "name": name})
            return

        # Declaracion de variable simple (primitiva)
        label = self._new_label(f"var_{name}")
        self._declare(name, {
            'label': label,
            'type': var_type,
            'is_array': False,
            'is_adt': False
        }, p)
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
        
        # Generacion de codigo para operaciones binarias usando la PILA (Stack).
        # 1. Se genera el codigo del operando izquierdo (resultado en R0).
        # 2. Se hace PUSH R0 para guardarlo.
        # 3. Se genera el codigo del operando derecho (resultado en R0).
        # 4. Se hace POP R1 para recuperar el izquierdo.
        # 5. Se opera R0 y R1.
        
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
        
        # Diccionario para operaciones aritmeticas y bitwise simples
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

        # Logica de comparacion
        lbl_true = self.get_new_label()
        lbl_end = self.get_new_label()
        lbl_false = self.get_new_label() + "_false"
        
        compare_logic = "CMP R1, R0\n"
        
        # Diccionario para instrucciones de salto basadas en comparacion
        # (jump_if_true, jump_if_false_check_needed)
        comparisons = {
            '==': (f"JZ {lbl_true}", False),
            '!=': (f"JNZ {lbl_true}", False),
            '<':  (f"JS {lbl_true}", False),
            '<=': (f"JS {lbl_true}\nJZ {lbl_true}", False),
            '>':  (f"JMP {lbl_true}", True), # Logica caso especial
            '>=': (f"JMP {lbl_true}", True)  # Logica caso especial
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
        
        entry = self._lookup(var_name)
        if not entry:
            # Si no se encuentra, asumir int y error (o dejar que _generate_var_access maneje el error)
            # _generate_var_access tambien usa _lookup ahora (lo actualizaremos)
            entry = {} 
        
        var_type = entry.get('type', 'int')

        if is_array_access:
            index_expr = p[3]
            index_code = index_expr[0]
            index_ast = index_expr[2]
            p[0] = (self._generate_array_access(var_name, index_code, p), var_type, {"type": "ArrayAccess", "array": var_name, "index": index_ast})
        else:
            p[0] = (self._generate_var_access(var_name, p), var_type, {"type": "Identifier", "name": var_name})

    def p_expression_member(self, p):
        """expression : ID DOT ID
                      | ID LBRACKET expression RBRACKET DOT ID"""
        if len(p) == 4:
            # ID.ID - Acceso a miembro de TDA
            obj = p[1]
            member = p[3]
            
            inst = self._lookup(obj)
            if not inst:
                self._error(f"Instancia TDA '{obj}' no declarada", p)
                p[0] = ("MOVI R0, 0", 'int', {"type": "Literal", "value": 0})
                return
                
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
        else:
            # ID[expr].ID - Acceso a miembro de elemento de array de TDA
            arr_name = p[1]
            index_expr = p[3]
            member_name = p[6]
            
            index_code = index_expr[0]
            index_ast = index_expr[2]
            
            entry = self._lookup(arr_name)
            if not entry or not entry.get('is_adt_array'):
                self._error(f"'{arr_name}' no es un array de TDA", p)
                p[0] = ("MOVI R0, 0", 'int', {"type": "ArrayMemberAccess", "array": arr_name, "index": index_ast, "member": member_name})
                return
                
            adt_info = entry.get('adt_info')
            if not adt_info or member_name not in adt_info['members']:
                self._error(f"Miembro '{member_name}' no encontrado en TDA", p)
                p[0] = ("MOVI R0, 0", 'int', {"type": "ArrayMemberAccess", "array": arr_name, "index": index_ast, "member": member_name})
                return
                
            member_info = adt_info['members'][member_name]
            member_offset = member_info.get('offset', 0) * 8  # Offset en bytes
            member_type = member_info.get('type', 'int')
            element_bytes = entry['element_size'] * 8
            
            # Calcular direccion del elemento
            base_label = entry['label']
            calc_offset = f"{index_code}\nMOVI R1, {element_bytes}\nMUL R1, R0, R1"
            
            if entry.get('is_param'):
                # Array dinamico
                addr_calc = f"{calc_offset}\nLD R2, [{base_label}]\nADD R15, R2, R1"
            else:
                # Array estatico
                addr_calc = f"{calc_offset}\nMOVI R2, {base_label}\nADD R15, R2, R1"
            
            # Cargar valor del miembro
            code = f"{addr_calc}\nLD R0, R15, {member_offset}"
            p[0] = (code, member_type, {"type": "ArrayMemberAccess", "array": arr_name, "index": index_ast, "member": member_name})

    def p_expression_func_call(self, p):
        """expression : func_call"""
        # func_call devuelve cadena de codigo. Necesitamos inferir el tipo.
        # Por ahora, asumir 'int' a menos que rastreemos tipos de retorno de funciones.
        # TODO: Rastrear tipos de retorno de funciones en tabla de simbolos.
        p[0] = (p[1][0], 'int', p[1][1])

    def p_expression_string(self, p):
        """expression : STRING"""
        # Generar etiqueta unica para cadena en seccion de datos
        self.string_count += 1
        str_label = f"STR_{self.string_count}"
        
        # Anadir cadena a seccion de datos usando directiva DB
        # Escapar la cadena apropiadamente y anadir terminador nulo
        string_content = p[1]
        self.data_section.append(f'{str_label}: DB "{string_content}", 0')
        
        # Devolver codigo para cargar direccion de cadena en R0
        p[0] = (f"MOVI R0, {str_label}", 'string', {"type": "Literal", "value": string_content})

    def p_expression_bool(self, p):
        """expression : TRUE
                      | FALSE"""
        val = True if p[1] == 'true' else False
        p[0] = ("MOVI R0, 1" if val else "MOVI R0, 0", 'bool', {"type": "Literal", "value": val})

    # Lista de parametros (restaurar reglas perdidas)
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
            # Parametro array: marcar como tupla para que p_func_decl sepa que es array
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
            # Llamada a funcion normal
            func_name = p[1]
            args = p[3] if p[3] else []
            
            ast_node = {"type": "Call", "function": func_name, "args": [arg[2] for arg in args]}

            # Funcion especial incorporada 'print' para imprimir sin nueva linea
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
                     # Float sin nueva linea: func=6 (subop=3)
                     p[0] = (f"{arg_code}\nOUT R0, 0xFFFF0008, 6", ast_node)
                else:
                     # Int sin nueva linea: func=4 (subop=2)
                     p[0] = (f"{arg_code}\nOUT R0, 0xFFFF0008, 4", ast_node)
                return

            # Construir codigo de empuje de argumentos - empujar en orden inverso para que el primer arg esté arriba
            args_code = ""
            if args:
                for arg_code, arg_type, arg_ast in reversed(args):
                    # Asegurar que arg_code termina con nueva linea
                    if not arg_code.endswith('\n'):
                        arg_code += '\n'
                    args_code += f"{arg_code}PUSH R0\n"
            
            # Registrar llamada para validacion posterior
            self.called_functions.add(func_name)
            
            p[0] = (f"{args_code}CALL FUNC_{func_name}", ast_node)
            
        else:
            # Llamada a metodo: obj.method(args)
            obj_name = p[1]
            method_name = p[3]
            args = p[5] if p[5] else []
            
            ast_node = {"type": "MethodCall", "object": obj_name, "method": method_name, "args": [arg[2] for arg in args]}
            
            obj_entry = self._lookup(obj_name)
            if not obj_entry:
                self._error(f"Objeto '{obj_name}' no declarado", p)
                p[0] = ("", ast_node)
                return
            
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
                self._error(f"Metodo '{method_name}' no encontrado en TDA '{adt_type}'", p)
                p[0] = ("", ast_node)
                return
            
            method_info = methods[method_name]
            
            # Comprobar visibilidad
            if method_info['visibility'] == 'private':
                # Permitir si dentro del mismo contexto TDA
                if self.current_context != adt_type:
                    self._error(f"Acceso ilegal a metodo privado '{method_name}' de '{adt_type}'", p)
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
            
            # Empujar 'this' (direccion del objeto)
            obj_label = obj_entry['label']
            this_code = f"MOVI R0, {obj_label}\nPUSH R0\n"
            
            mangled_label = method_info['label']
            p[0] = (f"{args_code}{this_code}CALL {mangled_label}", ast_node)

    # ==========================================================================
    # 6. FUNCIONES
    # ==========================================================================
    def p_func_decl(self, p):
        """func_decl : func_start statements ENDFUNC"""
        # Estructura de una funcion en ensamblador:
        # Etiqueta FUNC_nombre:
        #   POP R14 (Guardar direccion de retorno temporalmente)
        #   POP params... (Sacar argumentos de la pila y guardarlos en variables locales)
        #   PUSH R14 (Restaurar direccion de retorno para RET)
        #   ...cuerpo...
        #   RET
        
        func_name, params, param_setup, param_names, original_name = p[1]
        body_code, body_ast = p[2]
        
        # Asegurar que el cuerpo de la funcion no se mezcle con el codigo principal
        # Marcamos el inicio y fin claramente para el separador en p_program
        result = f"FUNC_{func_name}:\n{param_setup}{body_code}\n__END_FUNC__"
        
        # Salir del ambito de la funcion
        self._exit_scope()
        
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
            
            # Almacenar info del metodo
            self.current_adt_methods[func_name] = {
                'label': f"FUNC_{mangled_name}",
                'params': params.copy(), # Params originales antes de anadir 'this'
                'visibility': 'public' # Por defecto
            }
            
            # Anadir param 'this'
            # (type, name)
            params.insert(0, (self.current_context, 'this'))
            func_name = mangled_name
        
        # Registrar símbolo de funcion en el ambito actual (antes de entrar al de la funcion)
        self._declare(f"FUNC_{func_name}", {
            'type': 'function',
            'label': f"FUNC_{func_name}",
            'is_array': False,
            'is_adt': False,
            'params': params
        }, p)

        # Entrar a nuevo ambito para parametros y variables locales
        self._enter_scope()

        # Anadir parametros a la tabla de simbolos AHORA (antes de que se parsen las sentencias)
        # Despues de CALL, la pila tiene: [ret_addr] [arg1] [arg2] ...
        # El primer POP obtiene ret_addr (manejado por RET), asi que necesitamos saltarlo
        param_setup = ""
        param_names = []
        
        # Primero, sacar y guardar la direccion de retorno temporalmente
        param_setup += "POP R14\n"  # R14 = direccion de retorno
        
        # Ahora sacar parametros en orden normal (el primer param esta arriba)
        for param_type, param_name in params:
            is_array = False
            if isinstance(param_name, tuple):  # Parametro array
                param_name = param_name[0]
                is_array = True
            
            param_names.append(param_name)
            label = self._new_label(f"param_{param_name}")
            self._declare(param_name, {
                'label': label,
                'type': param_type,
                'is_array': is_array,
                'is_adt': False,
                'is_param': True  # Marcar como parametro
            }, p)
            self.data_section.append(f"{label}: DW 0")
            # Sacar parametro de la pila al almacenamiento
            param_setup += f"POP R0\nST R0, [{label}]\n"
        
        # Empujar direccion de retorno de vuelta para instrucción RET
        param_setup += "PUSH R14\n"
        
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
        # Siempre usar el resultado de la expresión (que maneja busqueda de ID vía _generate_var_access)
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
        # Inicio de declaracion de una Clase/Struct (TDA).
        # Prepara el contexto para que las funciones internas se traten como metodos
        # y tengan acceso implicito a 'this'.
        self.current_context = p[2]
        self.current_adt_members = {}
        self.current_adt_methods = {}
        self.current_adt_offset = 0
        p[0] = p[2]

    def p_adt_decl(self, p):
        """adt_decl : adt_head adt_body ENDADT"""
        adt_name = p[1]
        # raw_members contiene variables y metodos
        raw_members = [m for m in p[2] if m is not None]
        
        members_dict = {}
        method_code_list = []
        methods_ast = []
        members_ast = []
        
        for item in raw_members:
            name = item[0]
            if len(item) == 5 and item[0] == 'method':
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
        # Devolver el codigo de metodo acumulado
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
            # Anadir a miembros TDA actuales
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
        expr_type = expr[1]
        expr_ast = expr[2]
        
        kind = target[0]
        
        if kind == 'array':
            # target: ('array', arr_name, index_code, index_ast, lvalue_ast)
            arr_name = target[1]
            index_code = target[2]
            index_ast = target[3]
            
            # Validacion de tipo para array
            entry = self._lookup(arr_name)
            if entry:
                target_type = entry.get('type', 'int')
                if target_type != expr_type:
                    self._error(f"Error de tipo: No se puede asignar '{expr_type}' a elemento de array de tipo '{target_type}'", p)

            code = self._generate_array_assignment(arr_name, index_code, expr_code, p)
            ast = {"type": "ArrayAssignment", "target": arr_name, "index": index_ast, "value": expr_ast}
            p[0] = (code, ast)
            
        elif kind == 'array_member':
            # target: ('array_member', arr_name, index_code, index_ast, member_name, lvalue_ast)
            arr_name = target[1]
            index_code = target[2]
            index_ast = target[3]
            member_name = target[4]
            
            # Validacion de tipo para miembro de array de TDA
            entry = self._lookup(arr_name)
            if entry and entry.get('is_adt_array'):
                adt_info = entry.get('adt_info')
                if adt_info and member_name in adt_info['members']:
                    target_type = adt_info['members'][member_name].get('type', 'int')
                    if target_type != expr_type:
                        self._error(f"Error de tipo: No se puede asignar '{expr_type}' a miembro '{member_name}' de tipo '{target_type}'", p)

            code = self._generate_array_member_assignment(arr_name, index_code, member_name, expr_code, p)
            ast = {"type": "ArrayMemberAssignment", "array": arr_name, "index": index_ast, "member": member_name, "value": expr_ast}
            p[0] = (code, ast)
            
        elif kind == 'member':
            # target: ('member', obj_name, member_name, lvalue_ast)
            obj_name = target[1]
            member_name = target[2]
            
            # Validacion de tipo para miembro
            inst = self._lookup(obj_name)
            if inst and inst.get('is_adt'):
                members = inst.get('members', {})
                if member_name in members:
                    target_type = members[member_name].get('type', 'int')
                    if target_type != expr_type:
                        self._error(f"Error de tipo: No se puede asignar '{expr_type}' a miembro '{member_name}' de tipo '{target_type}'", p)

            code = self._generate_member_assignment(obj_name, member_name, expr_code, p)
            ast = {"type": "MemberAssignment", "object": obj_name, "member": member_name, "value": expr_ast}
            p[0] = (code, ast)
            
        elif kind == 'var':
            # target: ('var', name, lvalue_ast)
            name = target[1]
            
            # Validacion de tipo para variable
            entry = self._lookup(name)
            if entry:
                target_type = entry.get('type', 'int')
                if target_type != expr_type:
                    self._error(f"Error de tipo: No se puede asignar '{expr_type}' a variable '{name}' de tipo '{target_type}'", p)

            code = self._generate_var_assignment(name, expr_code, p)
            ast = {"type": "Assignment", "target": name, "value": expr_ast}
            p[0] = (code, ast)
            
        else:
            self._error("Objetivo de asignacion invalido", p)
            p[0] = ("", None)

    def p_lvalue(self, p):
        """lvalue : ID
                  | ID DOT ID
                  | ID LBRACKET expression RBRACKET
                  | ID LBRACKET expression RBRACKET DOT ID"""
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
        elif len(p) == 7:
            # ID[expr].ID - Acceso a miembro de elemento de array de TDA
            arr_name = p[1]
            index_expr = p[3]
            member_name = p[6]
            index_code = index_expr[0]
            index_ast = index_expr[2]
            p[0] = ('array_member', arr_name, index_code, index_ast, member_name, {"type": "ArrayMemberAccess", "array": arr_name, "index": index_ast, "member": member_name})

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
        
        # Declarar variable de iteración si no existe
        entry = self._lookup(var_name)
        if not entry:
            label = var_name
            self._declare(var_name, {
                'label': label,
                'type': 'int',
                'is_array': False,
                'is_adt': False
            }, p)
            self.data_section.append(f"{label}: DW 0")
        else:
            label = entry['label']
        
        lbl_start = self.get_new_label()
        lbl_end = self.get_new_label()
        self.loop_stack.append((lbl_start, lbl_end))
        
        init_code = f"{start_code}\nST R0, [{label}]"
        check_code = f"{end_code}\nPUSH R0\nLD R0, [{label}]\nPOP R1\nCMP R0, R1\nJS {lbl_start}_cont\nJMP {lbl_end}\n{lbl_start}_cont:"
        inc_code = f"LD R0, [{label}]\nMOVI R1, 1\nADD R0, R0, R1\nST R0, [{label}]"
        
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
    # Flujo de Control (Basico)
    # ----------------------------------------
    def p_if_stmt(self, p):
        """if_stmt : IF LPAREN expression RPAREN COLON statements ENDIF
                   | IF LPAREN expression RPAREN COLON statements ELSE COLON statements ENDIF"""
        
        # Generacion de etiquetas para control de flujo.
        # IF-ELSE:
        #   ...codigo condición...
        #   CMP R0, 0
        #   JZ label_else (Si es falso, salta al else)
        #   ...codigo true...
        #   JMP label_end
        # label_else:
        #   ...codigo else...
        # label_end:
        
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
            # Se agrega un salto de linea (ASCII 10) al final para consistencia con output numerico
            p[0] = (f"{expr_code}\nOUTS R0, 0xFFFF0008\nMOVI R0, 10\nOUT R0, 0xFFFF0000", ast)
        elif expr_type == 'float':
             # Usar OUT con func=6 (subop=3 -> print float)
             # 6 = (3 << 1) | 0
             p[0] = (f"{expr_code}\nOUT R0, 0xFFFF0008, 6", ast)
        else:
            # Usar OUT para salida numerica
            p[0] = (f"{expr_code}\nOUT R0, 0xFFFF0008", ast)

    def p_print_stmt(self, p):
        """statement : ID LPAREN expression RPAREN SEMI"""
        # Comprobar sintaxis "print(expr)" para imprimir sin nueva linea
        if p[1] == 'print':
            expr = p[3]
            expr_code = expr[0]
            expr_type = expr[1]
            expr_ast = expr[2]
            
            ast = {"type": "Call", "function": "print", "args": [expr_ast]}
            
            if expr_type == 'string':
                 p[0] = (f"{expr_code}\nOUTS R0, 0xFFFF0008", ast)
            elif expr_type == 'float':
                 # Usar OUT con func=6 (subop=3 -> print float)
                 p[0] = (f"{expr_code}\nOUT R0, 0xFFFF0008, 6", ast)
            else:
                 # Usar OUT con func=4 (subop=2 -> print int sin nueva linea)
                 # 4 = (2 << 1) | 0
                 p[0] = (f"{expr_code}\nOUT R0, 0xFFFF0008, 4", ast)
        else:
            # Retroceder a logica de llamada a funcion normal si no es 'print'
            # Pero espera, p_statement ya maneja func_call_stmt.
            # Esta regla podria entrar en conflicto.
            # Mejor anadir 'print' como palabra clave o manejarlo en func_call.
            p[0] = ("", None)
            
    # Manejaremos 'print' como una llamada a funcion especial en p_func_call


    def p_input_stmt(self, p):
        """input_stmt : INPUT ID SEMI"""
        var_name = p[2]
        ast = {"type": "Input", "variable": var_name}
        
        entry = self._lookup(var_name)
        if not entry:
             print(f"Error: Variable {var_name} no declarada.")
             p[0] = ("", ast)
             return
        label = entry['label'] if isinstance(entry, dict) and 'label' in entry else var_name
        p[0] = (f"IN R0, 0xFFFF0018\nST R0, [{label}]", ast)

    def p_empty(self, p):
        """empty :"""
        pass

    def p_error(self, p):
        self.error_count += 1
        if p:
            print(f"Error de sintaxis en '{p.value}' linea {p.lineno}")
        else:
            print("Error de sintaxis en EOF")

    def parse(self, code, lexer, library_asm=None):
        self.asm = ""
        self.label_count = 0
        self.string_count = 0
        self.scopes = [{}] # Reiniciar scopes
        self.data_section = []
        self.error_count = 0
        self.called_functions = set()
        result = self.parser.parse(code, lexer=lexer)
        
        # Validar llamadas a funciones
        for func_name in self.called_functions:
            func_label = f"FUNC_{func_name}"
            is_defined = self._lookup(f"FUNC_{func_name}") # Buscar en scopes
            is_library = func_label in self.library_functions
            
            if not is_defined and not is_library:
                print(f"[Error del Parser] Funcion '{func_name}' llamada pero no definida ni encontrada en librerias.")
                self.error_count += 1

        if self.error_count > 0:
            return None
            
        if result:
            asm_code, ast = result
            # Agregar codigo de librerias al final si existe
            if library_asm:
                asm_code += "\n\n# --- Library Functions ---\n" + library_asm
            
            # Definir inicio del Heap al final de todo el codigo (incluyendo librerias)
            asm_code += "\n\n__HEAP_START: DW 0\n"
            
            return asm_code, ast
            
        return result

    # ----------------------------------------
    # Metodos Auxiliares de Generacion
    # ----------------------------------------
    def _generate_array_access(self, var_name, index_code, p):
        """
        Genera codigo para acceder a un elemento de un array: base + (index * element_size).
        Maneja la diferencia entre arrays estaticos (direccion fija) y dinamicos (punteros).
        Para arrays de TDAs, devuelve la DIRECCIÓN del elemento (no el valor).
        """
        entry = self._lookup(var_name)
        if not entry:
            self._error(f"Array '{var_name}' no declarado", p)
            return "MOVI R0, 0"
            
        if not (isinstance(entry, dict) and entry.get('is_array')):
            self._error(f"'{var_name}' no es un array", p)
            return "MOVI R0, 0"
            
        base_label = entry['label']
        
        # Determinar tamaño del elemento
        if entry.get('is_adt_array'):
            # Array de TDA: cada elemento ocupa element_size * 8 bytes
            element_bytes = entry['element_size'] * 8
            calc_offset = f"{index_code}\nMOVI R1, {element_bytes}\nMUL R1, R0, R1"
            
            # Para TDAs, devolver DIRECCIÓN del elemento (no cargar valor)
            if entry.get('is_param'):
                # Array dinámico: base es puntero
                return f"{calc_offset}\nLD R2, [{base_label}]\nADD R0, R2, R1"
            else:
                # Array estático: base es etiqueta
                return f"{calc_offset}\nMOVI R2, {base_label}\nADD R0, R2, R1"
        else:
            # Array primitivo: cada elemento ocupa 8 bytes, cargar valor
            calc_offset = f"{index_code}\nMOVI R1, 8\nMUL R1, R0, R1"
            
            if entry.get('is_param'):
                # Direccion base es dinámica (pasada como param)
                return f"{calc_offset}\nLD R2, [{base_label}]\nADD R15, R2, R1\nLD R0, R15, 0"
            
            # Direccion base es etiqueta estatica
            return f"{calc_offset}\nMOVI R2, {base_label}\nADD R15, R2, R1\nLD R0, R15, 0"

    def _generate_var_access(self, var_name, p):
        """
        Genera codigo para leer una variable.
        Detecta automaticamente si se esta accediendo a un miembro de clase dentro de un metodo
        para inyectar el acceso a traves de 'this'.
        """
        # Comprobar acceso a miembro TDA vía 'this' implicito
        if self.current_context and var_name in self.current_adt_members:
            offset = self.current_adt_members[var_name]['offset']
            this_entry = self._lookup('this')
            if this_entry:
                this_label = this_entry['label']
                byte_offset = offset * 8
                # Cargar puntero 'this' luego cargar miembro en offset
                return f"LD R1, [{this_label}]\nLD R0, R1, {byte_offset}"

        entry = self._lookup(var_name)
        if not entry:
            print(f"Error: Variable {var_name} no declarada.")
            return "MOVI R0, 0"
        
        # Si es array, devolver direccion
        if isinstance(entry, dict) and entry.get('is_array'):
            label = entry['label']
            if entry.get('is_param'):
                return f"LD R0, [{label}]"
            else:
                return f"MOVI R0, {label}"

        # Marcador de valor de instancia TDA
        if isinstance(entry, dict) and entry.get('is_adt'):
            # Devolver la direccion base de la instancia
            label = entry.get('label', var_name)
            return f"MOVI R0, {label}"
        
        label = entry.get('label', var_name)
        return f"LD R0, [{label}]"

    def _generate_var_assignment(self, target, expr_code, p):
        # Comprobar asignacion a miembro TDA vía 'this' implicito
        if self.current_context and target in self.current_adt_members:
            offset = self.current_adt_members[target]['offset']
            this_entry = self._lookup('this')
            if this_entry:
                this_label = this_entry['label']
                byte_offset = offset * 8
                # Almacenar R0 en [this + offset]
                return f"{expr_code}\nLD R1, [{this_label}]\nST R0, R1, {byte_offset}"

        entry = self._lookup(target)
        if not entry:
            self._error(f"Variable '{target}' no declarada", p)
            return ""
            
        label = entry.get('label', target)
        return f"{expr_code}\nST R0, [{label}]"

    def _generate_array_assignment(self, arr_name, index_code, expr_code, p):
        entry = self._lookup(arr_name)
        if not entry:
            self._error(f"Array '{arr_name}' no declarado", p)
            return ""
            
        if not entry.get('is_array'):
            self._error(f"'{arr_name}' no es un array", p)
            return ""
            
        base_label = entry['label']
        
        # Determinar tamaño del elemento
        if entry.get('is_adt_array'):
            # Array de TDA: cada elemento ocupa element_size * 8 bytes
            element_bytes = entry['element_size'] * 8
            calc_offset = f"{index_code}\nMOVI R1, {element_bytes}\nMUL R1, R0, R1"
        else:
            # Array primitivo: cada elemento ocupa 8 bytes
            calc_offset = f"{index_code}\nMOVI R1, 8\nMUL R1, R0, R1"
        
        # Calcular direccion objetivo en R15
        if entry.get('is_param'):
            addr_calc = f"{calc_offset}\nLD R2, [{base_label}]\nADD R15, R2, R1"
        else:
            addr_calc = f"{calc_offset}\nMOVI R2, {base_label}\nADD R15, R2, R1"
            
        return f"{addr_calc}\nPUSH R15\n{expr_code}\nPOP R15\nST R0, R15, 0"

    def _generate_array_member_assignment(self, arr_name, index_code, member_name, expr_code, p):
        """Genera código para arr[i].member = value"""
        entry = self._lookup(arr_name)
        if not entry or not entry.get('is_adt_array'):
            self._error(f"'{arr_name}' no es un array de TDA", p)
            return ""
            
        adt_info = entry.get('adt_info')
        if not adt_info or member_name not in adt_info['members']:
            self._error(f"Miembro '{member_name}' no encontrado en TDA", p)
            return ""
            
        member_info = adt_info['members'][member_name]
        member_offset = member_info.get('offset', 0) * 8  # Offset en bytes
        element_bytes = entry['element_size'] * 8
        
        # Calcular dirección del elemento: base + (index * element_size)
        base_label = entry['label']
        calc_offset = f"{index_code}\nMOVI R1, {element_bytes}\nMUL R1, R0, R1"
        
        if entry.get('is_param'):
            # Array dinámico
            addr_calc = f"{calc_offset}\nLD R2, [{base_label}]\nADD R15, R2, R1"
        else:
            # Array estático
            addr_calc = f"{calc_offset}\nMOVI R2, {base_label}\nADD R15, R2, R1"
        
        # Sumar offset del miembro y almacenar valor
        return f"{addr_calc}\nPUSH R15\n{expr_code}\nPOP R15\nST R0, R15, {member_offset}"

    def _generate_member_assignment(self, obj, member, expr_code, p):
        inst = self._lookup(obj)
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


