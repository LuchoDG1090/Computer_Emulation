"""
Script simple para ensamblar y ejecutar programas assembly
Uso: python run_program.py <archivo.asm>
"""

import io
import sys
from pathlib import Path

# Configurar UTF-8 para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Añadir ruta del proyecto
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from src.assembler.assembler import Assembler
from src.cpu.cpu import CPU
from src.memory.loader import Loader


def main():
    if len(sys.argv) < 2:
        print("Uso: python run_program.py <archivo.asm>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"Error: El archivo '{input_file}' no existe")
        sys.exit(1)

    # Nombres de archivos
    base_name = Path(input_file).stem
    output_bin = f"build/{base_name}.bin"
    output_map = f"build/{base_name}.map"

    # Ensamblar
    assembler = Assembler()
    assembler.assemble_file(input_file, output_bin, output_map)

    # Ejecutar
    cpu = CPU()
    Loader.cargar_programa(cpu, output_bin, output_map)

    # Configurar entrada/salida
    cpu.io_ports.set_output_char_callback(lambda ch: print(chr(ch), end="", flush=True))
    cpu.io_ports.set_output_int_callback(lambda val: print(val, end="", flush=True))
    cpu.io_ports.set_input_int_callback(lambda: int(input()))

    # Configurar lectura de caracteres para líneas completas
    class InputBuffer:
        def __init__(self):
            self.buffer = []

        def read_char(self):
            if not self.buffer:
                line = input()
                self.buffer.extend(list(line + "\n"))
            return ord(self.buffer.pop(0)) if self.buffer else 10

    input_buf = InputBuffer()
    cpu.io_ports.set_input_char_callback(input_buf.read_char)

    # Ejecutar hasta 10000 ciclos
    for _ in range(10000):
        try:
            cpu.step()
        except:
            break


if __name__ == "__main__":
    main()
