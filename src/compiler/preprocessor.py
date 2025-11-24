import os
import re
import sys
import argparse

# Asegurar que el directorio 'src' esté en sys.path para usar el paquete local 'ply'
SRC_DIR = os.path.join(os.path.dirname(__file__), '..')
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

import ply.lex as lex

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
    t.lexer.skip(1)

lexer = lex.lex()

class MacroTable:
    def __init__(self):
        self.macros = {}

    def add(self, name, value):
        if name in self.macros:
            raise Exception(f"Macro duplicada: {name}")
        self.macros[name] = value

    def get(self, name):
        return self.macros.get(name)

    def replace_in_line(self, line):
        if not self.macros:
            return line

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
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[1]
                    value = ' '.join(parts[2:])
                    value = value.split('/*')[0].strip()
                    self.macros.add(name, value)
                return None

        return self.macros.replace_in_line(line)

    def _handle_include(self, filename, base_dir, system_file):
        search_dirs = self.include_paths if system_file else [base_dir] + self.include_paths

        for d in search_dirs:
            path = os.path.join(d, filename)
            if os.path.exists(path):
                return self._process_file(path, os.path.dirname(path))

        raise Exception(f"Archivo incluido no encontrado: {filename}")


# -------------------------------------------------------
# NUEVA FUNCIÓN PARA EJECUCIÓN TIPO "PIPELINE"
# -------------------------------------------------------
def preprocess_file_cli(input_path: str, output_dir: str) -> str:
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Archivo no encontrado: {input_path}")

    pre = Preprocessor()
    try:
        processed_code = pre.preprocess_file(input_path)
    except Exception as e:
        raise RuntimeError(f"Error en preprocesador: {e}")

    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_file = os.path.join(output_dir, base_name + "_preprocessed.txt")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(processed_code)

    return output_file


# -------------------------------------------------------
# MAIN CON ARGPARSE
# -------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Preprocesador de archivos con includes y macros")
    parser.add_argument("input", help="Ruta del archivo a preprocesar")
    parser.add_argument("--outdir", default="preprocessed", help="Directorio de salida")
    parser.add_argument("--show", action="store_true", help="Mostrar resultado por consola")

    args = parser.parse_args()

    try:
        output_path = preprocess_file_cli(args.input, args.outdir)
        print(f"Preprocesado exitoso. Archivo generado: {output_path}")

        if args.show:
            print("\n======= CÓDIGO PREPROCESADO =======\n")
            with open(output_path, 'r', encoding='utf-8') as f:
                print(f.read())

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
