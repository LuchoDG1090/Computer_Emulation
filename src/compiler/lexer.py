import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ply'))
import lex

# -------------------------------
# Palabras reservadas y sus tipos
# -------------------------------
reserved = {
    'if': 'IF', 'endif': 'ENDIF', 'else': 'ELSE',
    'while': 'WHILE', 'endwhile': 'ENDWHILE', 'break': 'BREAK', 'continue': 'CONTINUE',
    'for': 'FOR', 'endfor': 'ENDFOR',
    'func': 'FUNC', 'endfunc': 'ENDFUNC', 'return': 'RETURN',
    'output': 'OUTPUT', 'input': 'INPUT',
    'int': 'INT_TYPE', 'float': 'FLOAT_TYPE', 'string': 'STRING_TYPE',
    'bool': 'BOOL_TYPE', 'char': 'CHAR_TYPE', 'void': 'VOID_TYPE',
    'true': 'TRUE', 'false': 'FALSE',
    'adt': 'ADT', 'endadt': 'ENDADT', 'private': 'PRIVATE', 'public': 'PUBLIC',
    'in': 'IN',

    # Agentes comunicantes - Palabras clave
    'create': 'CREATE', 'agent': 'AGENT', 'move': 'MOVE',
    'link': 'LINK', 'unlink': 'UNLINK', 'send': 'SEND',
    'from': 'FROM', 'to': 'TO', 'on': 'ON', 'via': 'VIA',
    'agents': 'AGENTS', 'endagents': 'ENDAGENTS', 'run': 'RUN', 'step': 'STEP',
    
    # Agentes comunicantes - Estructura de mensajes
    'type': 'TYPE_KEY', 'payload': 'PAYLOAD_KEY', 'channel': 'CHANNEL_KEY',
    'origin': 'ORIGIN_KEY', 'destiny': 'DESTINY_KEY',
    
    # Agentes comunicantes - Tipos de mensajes
    'INFO': 'MSG_INFO', 'CHG_PARENT': 'MSG_CHG_PARENT',
    'DEL_LINK': 'MSG_DEL_LINK', 'CRE_LINK': 'MSG_CRE_LINK'
}

class MyLexer:
    # -------------------------------
    # Estados exclusivos
    # -------------------------------
    states = (
        ('comment', 'exclusive'),
        ('string', 'exclusive'),
    )

    # Contadores
    num_count = string_count = id_count = whitespace_count = kw_count = matched_count = 0

    # -------------------------------
    # Tokens
    # -------------------------------
    tokens = (
        'ID', 'INTEGER', 'FLOAT', 'STRING',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'INCREMENT', 'DECREMENT',
        'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE',
        'ASSIGN', 'AND', 'OR', 'NOT',
        'BIT_AND', 'BIT_OR', 'BIT_XOR', 'BIT_NOT', 'SHIFT_LEFT', 'SHIFT_RIGHT',
        'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET',
        'COMMA', 'COLON', 'SEMI', 'DOT', 'RANGE',

        # Agentes comunicantes - Estructuras
        'LBRACE', 'RBRACE',  # Llaves para JSON-like
        'ARROW',             # -> para enlaces
        'CHANNEL_ID',        # Identificador de canal: e_0, e_1, e_2, etc.
        
    ) + tuple(reserved.values())

    # -------------------------------
    # Comentarios multilínea
    # -------------------------------
    def t_begin_COMMENT_START(self, t):
        r'/\*'
        t.lexer.begin('comment')
        self.matched_count += 1
        self.whitespace_count += len(t.value)

    def t_comment_COMMENT_START(self, t):
        r'/\*'
        self.matched_count += 1
        self.whitespace_count += len(t.value)

    def t_comment_COMMENT_END(self, t):
        r'\*/'
        self.whitespace_count += len(t.value)
        self.matched_count -= 1
        if(self.matched_count < 0):
            print(f"Error lexico 01: unmatched */ en comentario multilínea (línea {t.lexer.lineno})")
            self.matched_count = 0
        if self.matched_count == 0: 
            t.lexer.begin('INITIAL')

    def t_comment_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self.whitespace_count += len(t.value)

    def t_comment_ANY(self, t):
        r'.'
        self.whitespace_count += 1

    def t_comment_eof(self, t):
        print(f"Error lexico: comentario multilínea no cerrado antes de EOF (línea {t.lexer.lineno})")

    def t_comment_error(self, t):
        self.whitespace_count += 1
        t.lexer.skip(1)

    # Comentarios de línea simple
    def t_ignore_COMMENT_SL(self, t):
        r'\#.*'
        self.whitespace_count += len(t.value)

    # Ignorar espacios y tabs
    def t_ignore_WHITESPACE(self, t):
        r'[ \t\f\v\r]+'
        self.whitespace_count += len(t.value)

    # -------------------------------
    # Operadores y delimitadores
    # -------------------------------
    t_ASSIGN = r'='
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_INCREMENT = r'\+\+'
    t_DECREMENT = r'--'
    t_EQ = r'=='
    t_NEQ = r'!='
    t_LT = r'<'
    t_LE = r'<='
    t_GT = r'>'
    t_GE = r'>='
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'
    t_BIT_AND = r'&'
    t_BIT_OR = r'\|'
    t_BIT_XOR = r'\^'
    t_BIT_NOT = r'~'
    t_SHIFT_LEFT = r'<<'
    t_SHIFT_RIGHT = r'>>'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COMMA = r','
    t_COLON = r':'
    t_SEMI = r';'
    t_DOT = r'\.'
    t_RANGE = r'\.\.'
    t_ARROW = r'->'

    # -------------------------------
    # Agentes comunicantes - Identificador de canal
    # -------------------------------
    def t_CHANNEL_ID(self, t):
        r'e_\d+'
        return t

    # -------------------------------
    # Identificadores y palabras reservadas
    # -------------------------------
    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        # Verificar si es una palabra reservada
        t.type = reserved.get(t.value, 'ID')
        
        if t.type == 'ID':
            # Validación de prefijo deshabilitada para permitir nombres libres
            self.id_count += 1
        else:
            # Es una palabra reservada
            self.kw_count += 1
        
        return t

    # Números
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?([eE][+-]?\d+)?'
        self.num_count += 1
        try:
            t.value = float(t.value) if '.' in t.value or 'e' in t.value.lower() else int(t.value)
            t.type = 'FLOAT' if isinstance(t.value, float) else 'INTEGER'
        except ValueError:
            print(f"Valor numerico invalido: {t.value}")
            t.value = 0
        return t

    # -------------------------------
    # Strings
    # -------------------------------
    def t_STRING_START(self, t):
        r'["\']'
        t.lexer.string_start = t.lexpos
        t.lexer.string_value = ''
        t.lexer.string_quote = t.value
        t.lexer.begin('string')

    def t_string_end(self, t):
        r'["\']'
        if t.value == t.lexer.string_quote:
            t.value = t.lexer.string_value
            t.type = 'STRING'
            self.string_count += 1
            t.lexpos = t.lexer.string_start
            t.lexer.begin('INITIAL')
            return t
        else:
            t.lexer.string_value += t.value

    def t_string_newline(self, t):
        r'\n'
        print(f"Error lexico: string no cerrado en la misma línea (línea {t.lexer.lineno})")
        t.lexer.lineno += 1
        t.lexer.begin('INITIAL')

    def t_string_any(self, t):
        r'.'
        t.lexer.string_value += t.value

    def t_string_eof(self, t):
        print(f"Error lexico: string no cerrado antes de EOF (línea {t.lexer.lineno})")

    def t_string_error(self, t):
        t.lexer.skip(1)

    # -------------------------------
    # Manejo de saltos de línea
    # -------------------------------
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        self.whitespace_count += len(t.value)

    # -------------------------------
    # Error de unmatched comment
    # -------------------------------
    def t_ignore_unmatched_comment(self, t):
        r'\*/'
        print(f"Error lexico 02: unmatched */ en comentario multilínea (línea {t.lexer.lineno})")

    # -------------------------------
    # Error léxico
    # -------------------------------
    def t_error(self, t):
        print(f"Error lexico: Caracter ilegal '{t.value[0]}' en linea {t.lineno}")
        t.lexer.skip(1)

    # -------------------------------
    # Construcción del lexer
    # -------------------------------
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        print("Lexer construido exitosamente")

    # -------------------------------
    # Probar archivo
    # -------------------------------
    def lexer_analysis(self, filepath):
        self.reset_counters()
        if not os.path.isfile(filepath):
            print(f"No se encontro el archivo: {filepath}")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            data = f.read()

        self.lexer.input(data)

        print(f"{'Tipo':<15} | {'Valor':<20} | {'Linea':<5} | {'Pos':<5}")
        print("-" * 55)

        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(f"{tok.type:<15} | {str(tok.value):<20} | {tok.lineno:<5} | {tok.lexpos:<5}")

        print("\n" + "="*50)
        self.info()

    # -------------------------------
    # Contadores
    # -------------------------------
    def reset_counters(self):
        self.num_count = self.string_count = self.id_count = self.kw_count = self.whitespace_count = self.matched_count = 0

    def info(self):
        print(f"Numeros: {self.num_count}")
        print(f"Strings: {self.string_count}")
        print(f"IDs: {self.id_count}")
        print(f"Keywords: {self.kw_count}")
        print(f"Espacios ignorados: {self.whitespace_count}")
        print(f"Total tokens significativos: {self.num_count + self.string_count + self.id_count + self.kw_count}")

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    archivo = input("Ingresa el nombre del archivo a analizar: ").strip()
    lexer = MyLexer()
    lexer.build()
    lexer.lexer_analysis(archivo)