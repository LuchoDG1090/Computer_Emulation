import sys
from pathlib import Path

# Agregar el directorio raíz al path para que las importaciones funcionen
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.assembler.assembler import Assembler

assembler = Assembler()

# Usar rutas relativas
input_file = ROOT_DIR / "programs" / "mcd_peña.asm"
output_bin = ROOT_DIR / "build" / "mcd_peña.bin"
output_map = ROOT_DIR / "build" / "mcd_peña.map"

try:
    assembler.assemble_file(
        input_file=str(input_file),
        output_binary=str(output_bin),
        output_map=str(output_map),
    )
except Exception as e:
    print(f"Error: {e}")
