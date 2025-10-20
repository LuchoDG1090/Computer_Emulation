import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path para que las importaciones funcionen
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.cpu.cpu import CPU
from src.memory.loader import Loader

# Deshabilitar logging
logging.disable(logging.CRITICAL)


def input_int_handler():
    """Callback para leer enteros desde la consola"""
    try:
        value = int(input())
        print(f"[INPUT] {value}")
        return value
    except ValueError:
        return 0


def output_int_handler(value):
    """Callback para mostrar enteros en la consola"""
    print(f"[OUTPUT] {value}")


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

print(f"PC inicial: 0x{cpu.pc:08X}")
print(f"Dirección de 'a': 0x{0x0BB8:08X}")
print(f"Dirección de 'b': 0x{0x2FF8:08X}\n")

# Ejecutar paso a paso
for i in range(50):
    print(
        f"[{i + 1}] PC=0x{cpu.pc:04X} | R1={cpu.registers[1]:4d} R2={cpu.registers[2]:4d} R3={cpu.registers[3]:4d} | [a]={cpu.mem.read_word(0x0BB8):4d} [b]={cpu.mem.read_word(0x2FF8):4d}"
    )

    try:
        should_continue = cpu.step()

        if not should_continue:
            print("\n[HALT]")
            break
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        break

print(f"\nCiclos: {cpu.cycle_count}, Resultado R1: {cpu.registers[1]}")
