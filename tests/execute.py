"""
Ejecutor de programas compilados
Uso: python execute.py <archivo.bin> <archivo.map>
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.cpu.cpu import CPU
from src.memory.loader import Loader


def execute_program(bin_path, map_path, max_cycles=100000):
    """
    Ejecuta un programa compilado usando el CPU y el loader

    Args:
        bin_path: Ruta al archivo .bin
        map_path: Ruta al archivo .map
        max_cycles: Numero maximo de ciclos de ejecucion
    """
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
    if len(sys.argv) < 3:
        print("Uso: python execute.py <archivo.bin> <archivo.map>")
        sys.exit(1)

    bin_path = sys.argv[1]
    map_path = sys.argv[2]

    try:
        cycles = execute_program(bin_path, map_path)
        print(f"\nEjecucion completada en {cycles} ciclos")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
