import os
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ply'))

import lex

tokens = [
    'INCLUDE_QUOTED',
    'INCLUDE_SYSTEM',
    'DEFINE',
    'IDENTIFIER',
    'VALUE',
]

# Reglas de tokens
t_INCLUDE_QUOTED = r'\#include\s+"[^"]+"'
t_INCLUDE_SYSTEM = r'\#include\s+<[^>]+>'
t_DEFINE = r'\#define'
t_ignore = ' \t'

def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    return t

def t_VALUE(t):
    r'[^#\n]+'
    t.value = t.value.strip()
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment(t):
    r'/\*\*+/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

class MacroTable:
    def __init__(self):
        self.macros = {}

    def add(self, name, value):
        """Agrega una nueva macro al diccionario"""
        if name in self.macros:
            raise Exception(f"Macro duplicada: {name}")
        self.macros[name] = value

    def get(self, name):
        """Devuelve el valor de una macro o None si no existe"""
        return self.macros.get(name)

    def replace_in_line(self, line):
        if not self.macros:
            return line

        # Crea un patrón que reconozca solo palabras completas que sean macros
        pattern = r'\b(' + '|'.join(map(re.escape, self.macros.keys())) + r')\b'

        def replacer(match):
            name = match.group(1)
            return self.macros[name]

        return re.sub(pattern, replacer, line)

class Preprocessor:
    def __init__(self):
        self.macros = MacroTable()
        self.include_paths = ['.', 'includes']
        self.processed_files = set()

    def preprocess_file(self, filename):
        """Preprocesa un archivo completo y devuelve el código expandido"""
        self.processed_files.clear()
        return self._process_file(filename, os.path.dirname(filename))

    def _process_file(self, filename, base_dir):
        if filename in self.processed_files:
            raise Exception(f"Inclusión cíclica: {filename}")

        self.processed_files.add(filename)

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise Exception(f"Archivo no encontrado: {filename}")

        output_lines = []
        for line in content.split('\n'):
            processed = self._process_line(line, base_dir)
            if processed is not None:
                output_lines.append(processed)

        return '\n'.join(output_lines)

    def _process_line(self, line, base_dir):
        lexer.input(line)

        for token in lexer:
            if token.type == 'INCLUDE_QUOTED':
                filename = token.value.split('"')[1]
                return self._handle_include(filename, base_dir, system_file=False)
            elif token.type == 'INCLUDE_SYSTEM':
                filename = token.value.split('<')[1].split('>')[0]
                return self._handle_include(filename, base_dir, system_file=True)
            elif token.type == 'DEFINE':
                # Ejemplo: #define PI 3.14
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[1]
                    value = ' '.join(parts[2:])
                    value = value.split('#')[0].strip() #Eliminamos comentarios que estén después del define
                    self.macros.add(name, value)
                return None  # no imprime la línea define

        # Si no hay directivas, reemplaza macros
        return self.macros.replace_in_line(line)

    def _handle_include(self, filename, base_dir, system_file):
        """Busca el archivo y lo procesa recursivamente"""
        search_dirs = self.include_paths if system_file else [base_dir] + self.include_paths

        for d in search_dirs:
            path = os.path.join(d, filename)
            if os.path.exists(path):
                return self._process_file(path, os.path.dirname(path))

        raise Exception(f"Archivo incluido no encontrado: {filename}")

if __name__ == "__main__":
    pre = Preprocessor()
    try:
        result = pre.preprocess_file("src/compiler/prueba_1.txt") #aqui se coloca el archivo de prueba
        print("===== CÓDIGO PREPROCESADO =====\n")
        print(result)
    except Exception as e:
        print("Error:", e)