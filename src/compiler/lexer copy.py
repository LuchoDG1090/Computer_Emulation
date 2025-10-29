# Enlace documentacion: https://ply.readthedocs.io/en/latest/ply.html
# http://www.dabeaz.com/ply/


import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ply'))
import lex

# Excepción personalizada para errores críticos de lexer
class CriticalLexerError(Exception):
    def __init__(self, message, line_number):
        self.message = message
        self.line_number = line_number
        super().__init__(f"{message} en línea {line_number}")

# Palabras reservadas y sus tipos de token
reserved = {
    # Condicionales
    'if': 'IF',
    'endif': 'ENDIF',
    'then': 'THEN',
    'else': 'ELSE',

    # Bucles
    'while': 'WHILE',
    'endwhile': 'ENDWHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'for': 'FOR',
    'endfor': 'ENDFOR',

    # Funciones
    'func': 'FUNC',
    'endfunc': 'ENDFUNC',
    'return': 'RETURN',

    'output': 'OUTPUT',
    'input': 'INPUT',

    # **TIPOS DE DATOS**
    'int': 'INT_TYPE',
    'float': 'FLOAT_TYPE', 
    'string': 'STRING_TYPE',
    'bool': 'BOOL_TYPE',
    'char': 'CHAR_TYPE',
    'void': 'VOID_TYPE',


    # **VALORES BOOLEANOS**
    'true': 'TRUE',
    'false': 'FALSE',
    
    #TO-DO: Implementacion Agentes Comunicantes Robin Milner
}


class MyLexer(object):
    # Contadores
    num_count = 0
    string_count = 0
    id_count = 0
    whitespace_count = 0
    kw_count = 0
    error_count = 0  # Contador de errores
    nested_comment_depth = 0
    
    # Configuración de comportamiento de errores
    stop_on_mismatch = True  # Detener en primer error de comentario


    states = (
        ('commentML', 'exclusive'),
        ('commentSL', 'exclusive'),
        # ('string', 'exclusive'),
    )


    tokens = (

        #Palabras reservadas'

        # IDENTIFICADORES Y LITERALES
        'ID', 'INTEGER', 'FLOAT', 'STRING',

        #TO-DO: A implementar: 'CHAR', 'HEX', 'BINARY'
        
        # OPERADORES ARITMeTICOS
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'POWER',
        'INCREMENT', 'DECREMENT',

        # OPERADORES DE COMPARACIoN
        'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE',

        # OPERADOR DE ASIGNACION
        'ASSIGN',
        
        # OPERADORES LoGICOS
        'AND', 'OR', 'NOT',

        # OPERADORES BIT A BIT
        'BIT_AND', 'BIT_OR', 'BIT_XOR', 'BIT_NOT',
        'SHIFT_LEFT', 'SHIFT_RIGHT',

        # **DELIMITADORES**
        'LPAREN', 'RPAREN',           # ( )
        'LBRACKET', 'RBRACKET',       # [ ]
        'LBRACE', 'RBRACE',           # { }
        'COMMA', 'COLON', 'SEMI', 'DOT', 'RANGE',

        # No necesitamos token especial si no retornamos nada

    ) + tuple(reserved.values())  # Agregar palabras reservadas


    # ============== COMENTARIOS =====================
    
    # ============== ESTADO de multiples lineas =====================

    # Inicio de comentario multilínea (estado INITIAL)
    def t_begin_commentML(self, t):
        r'/\*'
        if self.nested_comment_depth == 0:
            t.lexer.begin('commentML')
            t.lexer.comment_start_line = t.lexer.lineno
        self.nested_comment_depth += 1
        pass

    def t_commentML_nested_start(self, t):
        r'/\*'
        self.nested_comment_depth += 1
        pass

    # Saltos de línea dentro del comentario
    def t_commentML_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self.whitespace_count += len(t.value)  # Contar saltos de linea
        t.lexer.skip(0)

    # Contenido del comentario (cualquier cosa excepto *, /, y newlines)
    def t_commentML_content(self, t):
        r'[^*/\n]+'  # Excluir /, *, y \n para que las reglas específicas funcionen
        pass  # Ignorar contenido

    # Slash suelto que no es parte de /*
    def t_commentML_slash(self, t):
        r'/(?!\*)'  # / no seguido de *
        pass

    # Asterisco suelto que no cierra comentario
    def t_commentML_star(self, t):
        r'\*(?!/)'  # * no seguido de /
        pass

    # Final del comentario multilínea
    def t_commentML_end(self, t):
        r'\*/'
        self.nested_comment_depth -= 1
        if self.nested_comment_depth == 0:
            t.lexer.begin('INITIAL')  # Volver al estado inicial
        t.lexer.skip(1)  # No retornar token

    # Error en estado commentML (generalmente EOF sin cerrar)
    def t_commentML_eof(self, t):
        print(f"Error: comentario multilínea sin cerrar iniciado en línea {t.lexer.comment_start_line}")
        print(f"Se esperaba '*/' antes del final del archivo")
        self.error_count += 1
        t.lexer.skip(0)

    def t_commentML_error(self, t):
        print(f"Error lexico en comentario multilínea en linea {t.lineno}: Caracter ilegal '{t.value[0]}'")
        self.error_count += 1
        t.lexer.skip(0)

    # ============== Comentario de linea simple =====================
    # Comentario de linea simple
    def t_comment_sl(self, t):
        r'\#.*'  # . no acepta \n por defecto
        t.lexer.begin('commentSL')
        print(f"Comentario de línea simple iniciado en línea {t.lineno}")
        pass  # Ignorar comentario de línea

    def t_commentSL_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self.whitespace_count += len(t.value)  # Contar saltos de linea
        t.lexer.begin('INITIAL')  # Volver al estado inicial
        pass

    def t_commentSL_error(self, t):
        print(f"Error lexico en comentario de línea en linea {t.lineno}: Caracter ilegal '{t.value[0]}'")
        self.error_count += 1
        t.lexer.skip(0)

    # ====================== Espacios en blanco =============================
    def t_WHITESPACE(self, t):
        r'[ \t\f\v\r]+'  # Espacios, tabs, form feed, vertical tab, carriage return
        #r'\s+' # Alternativa: match [ \t\n\r\f\v]+
        self.whitespace_count += len(t.value)  # Contar caracteres individuales
        pass  # Ignorar espacios en blanco  



    # ============== ERRORES ESPECIALES (MÁXIMA PRIORIDAD) =====================
    
    # Cierre de comentario sin apertura - COMPORTAMIENTO CONFIGURABLE
    def t_ANY_unmatched_comment_close(self, t):
        r'\*/'
        print(f"Error: cierre de comentario '*/' en línea {t.lineno}")
        self.error_count += 1
        
        # CRÍTICO: Asegurar conteo correcto de líneas sin manipular lexpos
        # PLY debería manejar automáticamente el avance de posición
        # Solo necesitamos actualizar lineno si hay newline inmediatamente después
        remaining_input = t.lexer.lexdata[t.lexer.lexpos:]
        if remaining_input.startswith('\n'):
            # Hay un salto de línea inmediatamente después del */
            t.lexer.lineno += 0
            # NO modificar lexpos - dejar que PLY lo maneje
        
        if self.stop_on_mismatch:
            # Modo estricto: detener inmediatamente
            raise CriticalLexerError("Cierre de comentario sin apertura", t.lineno)
        # Modo permisivo: continuar procesando
        t.lexer.skip(0)  # Consumir '*/'


    # ============== OPERADORES (ORDEN IMPORTANTE) =====================
    
    # Operadores de mayor prioridad primero (patrones más largos)
    t_POWER     = r'\*\*'   # ** antes que *
    t_INCREMENT = r'\+\+'   # ++ antes que +
    t_DECREMENT = r'--'     # -- antes que -
    t_SHIFT_LEFT = r'<<'    # << antes que <
    t_SHIFT_RIGHT = r'>>'   # >> antes que >
    t_EQ        = r'=='     # == antes que =
    t_NEQ       = r'!='     # != antes que !
    t_LE        = r'<='     # <= antes que <
    t_GE        = r'>='     # >= antes que >
    t_AND       = r'&&'     # && antes que &
    t_OR        = r'\|\|'   # || antes que |
    t_RANGE     = r'\.\.'   # .. antes que .

    # Operadores simples (después de los compuestos)
    t_ASSIGN    = r'='
    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_TIMES     = r'\*'     # * - puede crear conflicto con */
    t_DIVIDE    = r'/'      # / - puede crear conflicto con */
    t_MOD       = r'%'
    t_LT        = r'<'
    t_GT        = r'>'
    t_NOT       = r'!'
    t_BIT_AND   = r'&'
    t_BIT_OR    = r'\|'
    t_BIT_XOR   = r'\^'
    t_BIT_NOT   = r'~'

    # Delimitadores
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_LBRACKET  = r'\['
    t_RBRACKET  = r'\]'
    t_LBRACE    = r'\{'
    t_RBRACE    = r'\}'
    t_COMMA     = r','
    t_COLON     = r':'
    t_SEMI      = r';'
    t_DOT       = r'\.'


    # Identificadores con manejo de palabras reservadas
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        
        # Verificar si es palabra reservada ANTES de incrementar contadores
        original_type = reserved.get(t.value, 'ID')
        
        if original_type == 'ID':
            # Es un identificador genuino
            self.id_count += 1
            t.type = 'ID'
        else:
            # Es una palabra reservada
            self.kw_count += 1
            t.type = original_type      
            
        return t

    def t_NUMBER(self, t):
        r'\d+(\.\d+)?([eE][+-]?\d+)?'  # Soporta enteros y flotantes (sin signo negativo aqui)
        self.num_count += 1
        try:
            if '.' in t.value or 'e' in t.value.lower():
                t.value = float(t.value)
                t.type = 'FLOAT'
            else:
                t.value = int(t.value)
                t.type = 'INTEGER'
        except ValueError:
            print(f"Valor numerico invalido: {t.value}")
            t.value = 0
        return t
    
    def t_STRING(self, t):
        r'\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\''
        # Remover comillas y procesar secuencias de escape
        t.value = t.value[1:-1].encode().decode('unicode_escape')
        self.string_count += 1
        return t


    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self.whitespace_count += len(t.value)  # Contar saltos de linea


    def t_error(self, t):
        print(f"Error lexico: Caracter ilegal '{t.value[0]}' en linea {t.lineno}")
        self.error_count += 1
        t.lexer.skip(1)  # Consumir el carácter problemático

    def build(self, **kwargs):
        try:
            self.lexer = lex.lex(module=self, **kwargs)
            print("Lexer construido exitosamente")
        except Exception as e:
            print(f"Error al construir el lexer: {e}")
            import traceback
            traceback.print_exc()
            raise

    def test(self, data):
        # Reiniciar contadores al inicio del test
        self.reset_counters()
        
        self.lexer.input(data)
        tokens_found = []
        
        try:
            while True:
                tok = self.lexer.token()
                if not tok:
                    break
                tokens_found.append(tok)
                
                # Mostrar información detallada sobre números de línea
                print(f"Token: {tok.type:<12} = '{tok.value}' en línea {tok.lineno} (pos: {tok.lexpos})")
                
        except CriticalLexerError as e:
            print(f"🛑 ANÁLISIS DETENIDO: {e}")
            print("   No se procesarán más tokens debido al error crítico")
        
        # Verificar si terminó en estado incorrecto (comentario sin cerrar)
        if hasattr(self.lexer, 'current_state') and callable(self.lexer.current_state):
            current_state = self.lexer.current_state()
            if current_state == 'commentML':
                print(f"⚠️ ADVERTENCIA: Archivo terminó con comentario multilínea sin cerrar")
                print(f"   Comentario iniciado en línea {getattr(self.lexer, 'comment_start_line', 'desconocida')}")
                self.error_count += 1
        
        # Mostrar estadisticas al final
        print("\n" + "="*50)
        self.info()
        return tokens_found

    def reset_counters(self):
        """Reinicia todos los contadores"""
        self.num_count = 0
        self.string_count = 0
        self.id_count = 0
        self.whitespace_count = 0
        self.kw_count = 0
        self.error_count = 0
        self.nested_comment_depth = 0

    def info(self):
        """Informacion obtenida del analisis lexico"""
        print(f"Numeros reconocidos: {self.num_count}")
        print(f"Strings reconocidos: {self.string_count}")
        print(f"Identificadores reconocidos: {self.id_count}")
        print(f"Palabras reservadas reconocidas: {self.kw_count}")
        print(f"Espacios en blanco ignorados: {self.whitespace_count}")
        print(f"Errores encontrados: {self.error_count}")
        print(f"Total de tokens significativos reconocidos: {self.num_count + self.string_count + self.id_count + self.kw_count}")
        print(f'Nested depth of comments: {self.nested_comment_depth}')


    def get_keyword_details(self, data):
        """Devuelve detalles especificos de las palabras reservadas encontradas"""
        self.reset_counters()
        self.lexer.input(data)
        
        found_keywords = {}
        found_identifiers = []
        
        while True:
            tok = self.lexer.token()
            if not tok:
                break
                
            if tok.type in reserved.values():
                # Es una palabra reservada
                if tok.value in found_keywords:
                    found_keywords[tok.value] += 1
                else:
                    found_keywords[tok.value] = 1
            elif tok.type == 'ID':
                # Es un identificador
                if tok.value not in found_identifiers:
                    found_identifiers.append(tok.value)
        
        return found_keywords, found_identifiers


# Test para verificar el conteo correcto de líneas después de */
simple_mismatch_test = """
# apapapapa \n\n
/*int x = 5;
*/
float y = 3.14;
bool flag = true;
@
@
*/"""
prueba_completa = [simple_mismatch_test]
 
if __name__ == "__main__":
    for prueba in prueba_completa:
        try:
            print(f"\n ======  Prueba (Modo Estricto) ===========")
            m = MyLexer()
            m.stop_on_mismatch = True  # Modo estricto
            m.build()
            
            # Prueba del lexer
            m.test(prueba)
            
        except Exception as e:
            print(f"Error durante la ejecucion: {e}")
        
        try:
            print(f"\n ====== Prueba (Modo Permisivo) - Debug Líneas ======")
            print("Contenido línea por línea:")
            lines = prueba.split('\n')
            for i, line in enumerate(lines, 1):
                print(f"  Línea {i}: '{line}'")
            print("-" * 50)
            
            m2 = MyLexer()
            m2.stop_on_mismatch = False  # Modo permisivo
            m2.build()
            
            # Prueba del lexer
            m2.test(prueba)
            
            # Detalles de palabras reservadas e identificadores
            keywords_found, identifiers_found = m2.get_keyword_details(prueba)
            
            print(f"\nPalabras reservadas encontradas:")
            for kw, count in keywords_found.items():
                print(f"   '{kw}': {count} vez(es)")
                
            print(f"\nIdentificadores unicos encontrados:")
            for identifier in identifiers_found:
                print(f"   '{identifier}'")
            
        except Exception as e:
            print(f"Error durante la ejecucion en modo permisivo: {e}")




pruebas_extra = [
"""
    func fibonacci(int n) 
    if (n <= 1) then
        return n
    endif
    
    int result = fibonacci(n-1) + fibonacci(n-2)
    return result
endfunc
""",
""""
# Variables y operaciones
int x = 10
float pi = 3.14159
string mensaje = "Hola mundo"
bool activo = true
""",
"""
# Bucle
for i = 1; i <= x; i++ 
    output("Numero: ", i)
endfor
""",
"""
while (activo)
    input(x)
    if (x == 0) then x = 'Hola \\t\\n'
        break
endif
"""
]