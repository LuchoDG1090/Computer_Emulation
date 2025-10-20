"""
Test de ejecución automático con datos predefinidos
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para que las importaciones funcionen
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.cpu.cpu import CPU
from src.memory.loader import Loader


class AutoInputHandler:
    """Maneja entradas predefinidas para tests automáticos"""

    def __init__(self, values):
        self.values = values
        self.index = 0

    def get_next_int(self):
        """Retorna el siguiente valor predefinido"""
        if self.index < len(self.values):
            value = self.values[self.index]
            self.index += 1
            print(f"Input automático: {value}")
            return value
        return 0


def output_int_handler(value):
    """Callback para mostrar enteros en la consola"""
    print(f"Resultado: {value}")


# Valores predefinidos para el test (por ejemplo, MCD de 48 y 18 = 6)
auto_input = AutoInputHandler([48, 18])

cpu = CPU()

# Configurar callbacks de I/O
cpu.io_ports.set_input_int_callback(auto_input.get_next_int)
cpu.io_ports.set_output_int_callback(output_int_handler)

# Cargar programa usando rutas relativas
bin_path = ROOT_DIR / "build" / "mcd_peña.bin"
map_path = ROOT_DIR / "build" / "mcd_peña.map"

Loader().cargar_programa(
    cpu,
    str(bin_path),
    str(map_path),
)

# Ejecutar
print("Ejecutando programa MCD...")
cpu.run()

print(f"\nEjecución completada en {cpu.cycle_count} ciclos")
print(f"Registros finales: R1={cpu.registers[1]}, R2={cpu.registers[2]}")
