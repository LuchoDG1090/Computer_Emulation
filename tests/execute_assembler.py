"""Herramienta unificada: compilar .asm y opcionalmente ejecutar.

Uso básico:
  python compile.py <archivo.asm> <directorio_salida>

Ejecutar tras compilar:
  python compile.py <archivo.asm> <directorio_salida> --run [--max-cycles N]
"""

import sys
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.assembler.assembler import Assembler
from src.cpu.cpu import CPU
from src.memory.loader import Loader


def compile_asm(input_file: str, output_dir: str = "build"):
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"El archivo '{input_file}' no existe")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    base_name = input_path.stem
    output_bin = output_path / f"{base_name}.bin"
    output_map = output_path / f"{base_name}.map"

    assembler = Assembler()
    assembler.assemble_file(str(input_path), str(output_bin), str(output_map))
    return str(output_bin), str(output_map)


def execute_program(bin_path: str, map_path: str, max_cycles: int = 100000) -> int:
    bin_file = Path(bin_path)
    map_file = Path(map_path)
    if not bin_file.exists():
        raise FileNotFoundError(f"El archivo '{bin_path}' no existe")
    if not map_file.exists():
        raise FileNotFoundError(f"El archivo '{map_path}' no existe")

    cpu = CPU()
    Loader.cargar_programa(cpu, str(bin_file), str(map_file))

    cpu.io_ports.set_output_char_callback(lambda ch: print(chr(ch), end="", flush=True))
    cpu.io_ports.set_output_int_callback(lambda val: print(val, end="", flush=True))
    cpu.io_ports.set_input_int_callback(lambda: int(input()))

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

    try:
        for _ in range(max_cycles):
            if not cpu.step():
                break
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida")
    return cpu.cycle_count


def main():
    parser = argparse.ArgumentParser(description="Compilar archivo .asm y opcionalmente ejecutar")
    parser.add_argument("archivo", help="Ruta al .asm")
    parser.add_argument("directorio", help="Directorio salida compilacion (.bin/.map)")
    parser.add_argument("--run", action="store_true", help="Ejecutar tras compilar")
    parser.add_argument("--max-cycles", type=int, default=100000, help="Limite de ciclos de ejecucion")

    args = parser.parse_args()

    try:
        bin_path, map_path = compile_asm(args.archivo, args.directorio)
        print(f"Compilacion OK: {bin_path} | {map_path}")
        if args.run:
            cycles = execute_program(bin_path, map_path, args.max_cycles)
            print(f"\nEjecucion completada en {cycles} ciclos")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
