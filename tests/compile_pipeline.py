import os
import sys
import argparse

# Aseguramos que el root del repositorio esté en el path antes de imports locales
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.compiler.preprocessor import Preprocessor
from src.compiler.lexer import MyLexer
from src.compiler.parser import MyParser
from src.assembler.assembler import Assembler
from src.cpu.cpu import CPU
from src.memory.loader import Loader


def compile_file(input_path: str, output_dir: str) -> str:
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Archivo de entrada no encontrado: {input_path}")

    # 1. Preprocesador
    pre = Preprocessor()
    try:
        preprocessed_code = pre.preprocess_file(input_path)
    except Exception as e:
        raise RuntimeError(f"Error en preprocesador: {e}")

    # 2. Lexer
    lexer_instance = MyLexer()
    lexer_instance.build()
    lexer_instance.lexer.input(preprocessed_code)

    # 3. Parser
    parser = MyParser(MyLexer.tokens)
    try:
        result = parser.parse(preprocessed_code, lexer_instance.lexer)
        if result:
            asm_code, ast = result
        else:
            asm_code = None
    except Exception as e:
        raise RuntimeError(f"Error en parser: {e}")

    if not asm_code:
        raise RuntimeError("No se generó código ensamblador (ASM).")

    # Aseguramos directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_file = os.path.join(output_dir, base_name + '.asm')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(asm_code)

    return output_file


def assemble_asm(asm_path: str, build_dir: str) -> tuple:
    """Compila un .asm generado a bin/map usando el Assembler."""
    base_name = os.path.splitext(os.path.basename(asm_path))[0]
    os.makedirs(build_dir, exist_ok=True)
    bin_out = os.path.join(build_dir, f"{base_name}.bin")
    map_out = os.path.join(build_dir, f"{base_name}.map")
    assembler = Assembler()
    assembler.assemble_file(asm_path, bin_out, map_out)
    return bin_out, map_out


def execute_binary(bin_path: str, map_path: str, max_cycles: int = 100000) -> int:
    cpu = CPU()
    Loader.cargar_programa(cpu, bin_path, map_path)
    cpu.io_ports.set_output_char_callback(lambda ch: print(chr(ch), end="", flush=True))
    cpu.io_ports.set_output_int_callback(lambda val: print(val, end="", flush=True))
    class InputBuffer:
        def __init__(self):
            self.buffer = []
            self.int_buffer = []

        def read_char(self):
            if not self.buffer:
                try:
                    line = input()
                    self.buffer.extend(list(line + "\n"))
                except EOFError:
                    return 0
            return ord(self.buffer.pop(0)) if self.buffer else 10

        def read_int(self):
            while not self.int_buffer:
                try:
                    line = input()
                    # Split by whitespace and filter empty strings
                    tokens = line.strip().split()
                    for token in tokens:
                        try:
                            self.int_buffer.append(int(token))
                        except ValueError:
                            pass # Ignore non-integer tokens
                except EOFError:
                    return 0
            return self.int_buffer.pop(0)

    input_buf = InputBuffer()
    cpu.io_ports.set_input_char_callback(input_buf.read_char)
    cpu.io_ports.set_input_int_callback(input_buf.read_int)

    try:
        for _ in range(max_cycles):
            if not cpu.step():
                break
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida")
    return cpu.cycle_count


def main():
    parser = argparse.ArgumentParser(description="Pipeline: HL -> ASM (+ opcional ensamblar y ejecutar)")
    parser.add_argument('input', help='Archivo fuente alto nivel (.txt)')
    parser.add_argument('--outdir', default=os.path.join(ROOT_DIR, 'programs'), help='Directorio salida ASM (default ./programs)')
    parser.add_argument('--builddir', default=os.path.join(ROOT_DIR, 'build/relocatables'), help='Directorio salida bin/map (default ./build/relocatables)')
    parser.add_argument('--show', action='store_true', help='Mostrar ASM generado')
    parser.add_argument('--assemble', action='store_true', help='Generar bin/map tras ASM')
    parser.add_argument('--run', action='store_true', help='Ejecutar tras ensamblar')
    parser.add_argument('--max-cycles', type=int, default=100000, help='Limite de ciclos para ejecucion')

    args = parser.parse_args()

    try:
        asm_path = compile_file(args.input, args.outdir)
        print(f"ASM generado: {asm_path}")
        if args.show:
            with open(asm_path, 'r', encoding='utf-8') as f:
                print("\n===== ASM =====\n")
                print(f.read())
        bin_path = map_path = None
        if args.assemble or args.run:
            bin_path, map_path = assemble_asm(asm_path, args.builddir)
        if args.run:
            cycles = execute_binary(bin_path, map_path, args.max_cycles)
            print(f"\nEjecucion completada en {cycles} ciclos")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
