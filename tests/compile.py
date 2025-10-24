"""
Compilador de archivos assembly a código reubicable
Uso: python compile.py <archivo.asm>
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.assembler.assembler import Assembler


def compile_asm(input_file, output_dir="build"):
    """
    Compila un archivo .asm a código reubicable (.bin y .map)

    Args:
        input_file: Ruta al archivo .asm
        output_dir: Directorio donde guardar los archivos generados

    Returns:
        tuple: (ruta_bin, ruta_map)
    """
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


def main():
    if len(sys.argv) < 2:
        print("Uso: python compile.py <archivo.asm>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        compile_asm(input_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
