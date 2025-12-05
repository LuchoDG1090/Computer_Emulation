import os
import re
import sys
import argparse

# Asegurar que el directorio 'src' esté en sys.path para usar el paquete local 'ply'
# Y también el directorio raíz para importar 'src.compiler.library_loader'
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

SRC_DIR = os.path.join(os.path.dirname(__file__), '..')
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

import ply.lex as lex
from src.compiler.library_loader import LibraryLoader
from src.disk.simple_disk import SimpleDisk

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
    def __init__(self, disk_path: str = "disk.img"):
        self.macros = MacroTable()
        self.include_paths = ['.']  # Solo directorio actual para includes con comillas
        self.processed_files = set()
        self.library_loader = LibraryLoader()
        self.smart_includes = []  # Lista de rutas de librerías ASM detectadas
        self.disk = SimpleDisk(disk_path)  # Disco virtual para programas precompilados

    def preprocess_file(self, filename):
        self.processed_files.clear()
        self.smart_includes.clear()
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
        """
        Maneja directivas #include.
        
        - #include <library>: Busca SOLO en disk.img (programas precompilados)
        - #include "file.txt": Busca en directorio local
        """
        
        if system_file:
            # Include de sistema: buscar ÚNICAMENTE en disco virtual
            asm_code = self.disk.read_program(filename)
            
            if asm_code:
                # Programa encontrado en disco
                print(f"\033[36m[Preprocessor] Cargando '{filename}' desde disk.img\033[0m")
                self.smart_includes.append((filename, asm_code))
                return ""  # Eliminar línea de include del código fuente
            else:
                # No encontrado en disco - ERROR (sin fallback a includes/)
                raise Exception(
                    f"Programa '{filename}' no encontrado en disco virtual.\n"
                    f"  Sugerencia: Compila la librería y añádela al disco con:\n"
                    f"    python tools/disk_manager.py write {filename} <archivo.asm>"
                )
        else:
            # Include con comillas: buscar en directorio local
            search_dirs = [base_dir] + self.include_paths
            
            for d in search_dirs:
                path = os.path.join(d, filename)
                if os.path.exists(path):
                    print(f"\033[36m[Preprocessor] Incluyendo '{filename}' desde {d}\033[0m")
                    return self._process_file(path, os.path.dirname(path))
            
            raise Exception(f"Archivo incluido no encontrado: {filename}")

    def get_smart_includes_asm(self, source_code):
        """
        Procesa smart includes desde disco virtual.
        
        Para cada librería incluida desde disk.img, extrae solo las funciones
        que realmente se usan en el código fuente.
        
        Args:
            source_code: Código fuente preprocesado
        
        Returns:
            Código ASM combinado de todas las funciones usadas
        """
        combined_asm = []
        
        for item in self.smart_includes:
            # Los smart includes ahora son tuplas (nombre, asm_code) desde disk.img
            if isinstance(item, tuple):
                lib_name, asm_code = item
                
                # Analizar el código ASM para extraer funciones
                # (usar LibraryLoader para parsear funciones del código ASM en memoria)
                import tempfile
                
                # Crear archivo temporal para que LibraryLoader lo procese
                with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False, encoding='utf-8') as tmp:
                    tmp.write(asm_code)
                    tmp_path = tmp.name
                
                try:
                    available_funcs = self.library_loader.get_defined_functions(tmp_path)
                    
                    for func in available_funcs:
                        # Manejar convención FUNC_
                        search_name = func
                        if func.startswith("FUNC_"):
                            search_name = func[5:]
                        
                        # Buscar uso de la función en el código
                        pattern = r'\b' + re.escape(search_name) + r'\s*\('
                        if re.search(pattern, source_code):
                            func_code = self.library_loader.get_function_code(tmp_path, func)
                            combined_asm.append(f"# --- Begin {search_name} from {lib_name} ---")
                            combined_asm.append(func_code)
                            combined_asm.append(f"# --- End {search_name} ---")
                finally:
                    # Limpiar archivo temporal
                    os.unlink(tmp_path)
            else:
                # Compatibilidad con includes antiguos (rutas de archivos)
                lib_path = item
                available_funcs = self.library_loader.get_defined_functions(lib_path)
                
                for func in available_funcs:
                    search_name = func
                    if func.startswith("FUNC_"):
                        search_name = func[5:]
                    
                    pattern = r'\b' + re.escape(search_name) + r'\s*\('
                    if re.search(pattern, source_code):
                        asm_code = self.library_loader.get_function_code(lib_path, func)
                        combined_asm.append(f"# --- Begin {search_name} from {os.path.basename(lib_path)} ---")
                        combined_asm.append(asm_code)
                        combined_asm.append(f"# --- End {search_name} ---")
        
        return "\n".join(combined_asm)

    def get_available_library_functions(self):
        """
        Devuelve un conjunto con los nombres de todas las funciones disponibles
        en las librerías incluidas desde disco virtual.
        """
        available_funcs = set()
        
        import tempfile
        
        for item in self.smart_includes:
            if isinstance(item, tuple):
                # Smart include desde disco: (nombre, asm_code)
                lib_name, asm_code = item
                
                # Crear archivo temporal para analizar
                with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False, encoding='utf-8') as tmp:
                    tmp.write(asm_code)
                    tmp_path = tmp.name
                
                try:
                    funcs = self.library_loader.get_defined_functions(tmp_path)
                    available_funcs.update(funcs)
                finally:
                    os.unlink(tmp_path)
            else:
                # Include tradicional (archivo)
                funcs = self.library_loader.get_defined_functions(item)
                available_funcs.update(funcs)
        
        return available_funcs


# -------------------------------------------------------
# FUNCIÓN PARA EJECUCIÓN TIPO "PIPELINE"
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
