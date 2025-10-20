import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path para que las importaciones funcionen
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.cpu.core import Flags
from src.cpu.cpu import CPU
from src.memory.loader import Loader

# Deshabilitar logging
logging.disable(logging.CRITICAL)


def get_flag_name(flag_bit):
    """Convierte número de bit a nombre de flag"""
    names = {0: "ZERO", 1: "CARRY", 2: "NEGATIVE", 3: "POSITIVE", 4: "OVERFLOW"}
    return names.get(flag_bit, f"BIT{flag_bit}")


def print_flags(flags):
    """Imprime los flags activos"""
    active = []
    for i in range(8):
        if flags & (1 << i):
            active.append(get_flag_name(i))
    return " | ".join(active) if active else "NONE"


def input_int_handler():
    return int(input())


def output_int_handler(value):
    print(f"[OUTPUT] {value}")


cpu = CPU()
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

print("Ejecutando primeros ciclos para verificar flags:\n")

# Ejecutar hasta el bucle principal
for i in range(20):
    pc_before = cpu.pc
    flags_before = cpu.flags

    should_continue = cpu.step()

    print(
        f"[{i + 1:2d}] PC: 0x{pc_before:04X} -> 0x{cpu.pc:04X} | "
        f"R1={cpu.registers[1]:5d} R2={cpu.registers[2]:5d} R3={cpu.registers[3]:6d} | "
        f"Flags: {print_flags(cpu.flags)}"
    )

    if not should_continue:
        break

print("\nFlags después de ciclo 9 (debería tener NEGATIVE activo):")
print(f"  R3 = {cpu.registers[3]} (debería ser -512 en signed)")
print(f"  Flags = 0b{cpu.flags:08b} = {print_flags(cpu.flags)}")
print(f"  NEGATIVE está activo: {bool(cpu.flags & (1 << Flags.NEGATIVE))}")
