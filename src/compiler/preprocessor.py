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
    def __init__(self, prefer_text_for_bin: bool = False):
        self.macros = MacroTable()
        self.include_paths = ['.', 'includes']
        self.processed_files = set()
        # When True, prefer a text (.txt) fallback for includes that point at
        # a binary (.bin) sibling. If False, inline binary data verbatim.
        self.prefer_text_for_bin = prefer_text_for_bin

    def preprocess_file(self, filename):
        self.processed_files.clear()
        return self._process_file(filename, os.path.dirname(filename))

    def _process_file(self, filename, base_dir):
        if filename in self.processed_files:
            raise Exception(f"Inclusión cíclica: {filename}")

        self.processed_files.add(filename)

        if not os.path.exists(filename):
            raise Exception(f"Archivo no encontrado: {filename}")

        # If .bin file — return raw bytes
        if filename.lower().endswith('.bin'):
            with open(filename, 'rb') as bf:
                return bf.read()

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        produced = []  # elements are str or bytes
        for line in content.split('\n'):
            processed = self._process_line(line, base_dir)
            if processed is not None:
                produced.append(processed)

        # If any produced element is bytes, assemble a bytes result with raw binary inserts
        if any(isinstance(p, (bytes, bytearray)) for p in produced):
            out_parts = []
            for i, part in enumerate(produced):
                next_part = produced[i+1] if i+1 < len(produced) else None

                if isinstance(part, (bytes, bytearray)):
                    out_parts.append(bytes(part))
                    # Do not insert extra newlines around binary blocks to keep them verbatim
                else:
                    # encode text; add newline between text pieces (but not around binary)
                    out_parts.append(part.encode('utf-8'))
                    if isinstance(next_part, str):
                        out_parts.append(b'\n')

            return b''.join(out_parts)

        # All text — join with newlines as before
        return '\n'.join(map(str, produced))

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

            # Prefer a binary counterpart (e.g., Foo.bin) if present — even
            # when a text file with the included name exists. This enforces the
            # teacher's requirement that included files be binary.
            base, _ext = os.path.splitext(path)
            bin_candidate = base + '.bin'
            txt_candidate = base + '.txt'

            # If the include explicitly names a .bin file, treat it as
            # a binary include — inline it verbatim (don't prefer text)
            if filename.lower().endswith('.bin'):
                if os.path.exists(path):
                    return self._inline_binary_file(path)
                else:
                    # explicit .bin requested but not found here; continue
                    continue

            # If the bin counterpart exists, and we prefer text, try to
            # find a .txt fallback first (either alongside or inside backups).
            if os.path.exists(bin_candidate):
                if self.prefer_text_for_bin:
                    # Look for .txt in the same search directory
                    if os.path.exists(txt_candidate):
                        path = txt_candidate
                    else:
                        # Look for a global backup copy if present
                        bak = os.path.join(os.path.dirname(__file__), '..', '..', 'backups', 'preprocessor_txt', os.path.basename(txt_candidate))
                        if os.path.exists(bak):
                            path = bak
                        else:
                            # No .txt fallback — use the .bin
                            path = bin_candidate
                else:
                    path = bin_candidate
            elif not os.path.exists(path):
                # If neither exact filename nor .bin exists, continue searching
                # other include directories.
                continue

            if os.path.exists(path):
                # If the file is a binary file (ends with .bin) or cannot be
                # decoded as UTF-8, read it as bytes and include it verbatim
                # into the preprocessed output so that includes become raw
                # binary code in the result.
                if path.lower().endswith('.bin'):
                    return self._inline_binary_file(path)

                # Otherwise treat as text and recurse into it
                try:
                    # Try opening in text mode. If decoding fails, fall back to
                    # binary handling above.
                    return self._process_file(path, os.path.dirname(path))
                except UnicodeDecodeError:
                    with open(path, 'rb') as bf:
                        raw = bf.read()
                    return raw
        raise Exception(f"Archivo incluido no encontrado: {filename}")

    def _inline_binary_file(self, path: str) -> bytes:
        """Read a binary include and return its raw bytes."""
        with open(path, 'rb') as bf:
            return bf.read()


# -------------------------------------------------------
# NUEVA FUNCIÓN PARA EJECUCIÓN TIPO "PIPELINE"
# -------------------------------------------------------
def preprocess_file_cli(input_path: str, output_dir: str, prefer_text_for_bin: bool = True) -> str:
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Archivo no encontrado: {input_path}")

    pre = Preprocessor(prefer_text_for_bin=prefer_text_for_bin)
    try:
        processed_code = pre.preprocess_file(input_path)
    except Exception as e:
        raise RuntimeError(f"Error en preprocesador: {e}")

    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]

    # If the processed result is bytes, write a binary output file. Otherwise
    # write a text output (same behavior as before).
    if isinstance(processed_code, (bytes, bytearray)):
        output_file = os.path.join(output_dir, base_name + "_preprocessed.bin")
        with open(output_file, 'wb') as f:
            f.write(processed_code)
    else:
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--force-binary", action="store_true", help="Inline binary includes verbatim (no text fallback)")
    group.add_argument("--prefer-text", action="store_true", help="Prefer text fallbacks for binary-capable includes (overrides default)")
    parser.add_argument("--show", action="store_true", help="Mostrar resultado por consola")

    args = parser.parse_args()

    try:
        # Default behavior: prefer binary includes (prefer_text_for_bin=False)
        if args.prefer_text:
            prefer_text = True
        elif args.force_binary:
            prefer_text = False
        else:
            prefer_text = False

        output_path = preprocess_file_cli(args.input, args.outdir, prefer_text_for_bin=prefer_text)
        print(f"Preprocesado exitoso. Archivo generado: {output_path}")

        if args.show:
            print("\n======= CÓDIGO PREPROCESADO =======\n")
            # If the preprocessed file is binary, show a short preview instead
            # of trying to decode the whole thing as text.
            if output_path.lower().endswith('.bin'):
                with open(output_path, 'rb') as f:
                    data = f.read(256)
                print(f"<binary file: {len(data)} bytes shown (first 256 bytes)>\n", data)
            else:
                with open(output_path, 'r', encoding='utf-8') as f:
                    print(f.read())

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
