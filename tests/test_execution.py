import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path para que las importaciones funcionen
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.cpu.cpu import CPU
from src.memory.loader import Loader

# Deshabilitar logging para evitar bug de Python 3.13
logging.disable(logging.CRITICAL)


def input_int_handler():
    """Callback para leer enteros desde la consola"""
    try:
        value = int(input())  # Sin mensaje - el programa assembly debe definirlo
        return value
    except ValueError:
        return 0


def output_int_handler(value):
    """Callback para mostrar enteros en la consola"""
    print(value)


cpu = CPU()

# Configurar callbacks de I/O
cpu.io_ports.set_input_int_callback(input_int_handler)
cpu.io_ports.set_output_int_callback(output_int_handler)

# Cargar programa usando rutas relativas
bin_path = ROOT_DIR / "build" / "mcd_peña.bin"
map_path = ROOT_DIR / "build" / "mcd_peña.map"

Loader().cargar_programa(
    cpu,
    str(bin_path),
    str(map_path),
)

# Ejecutar con límite de ciclos para evitar loops infinitos
try:
    cpu.run(max_cycles=10000)
except KeyboardInterrupt:
    print("\n[Interrumpido por usuario]")

print(f"\nEjecución completada en {cpu.cycle_count} ciclos")
