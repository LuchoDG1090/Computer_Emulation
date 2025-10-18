"""Generador de mapas de memoria"""


class MemoryMap:
    """Gestiona el mapa de memoria ejecutable"""

    def __init__(self):
        self.executable_addresses = set()
        self.data_addresses = set()

    def mark_executable(self, address):
        """Marca una dirección como ejecutable"""
        self.executable_addresses.add(address)

    def mark_data(self, address):
        """Marca una dirección como datos"""
        self.data_addresses.add(address)

    def is_executable(self, address):
        """Verifica si una dirección es ejecutable"""
        return address in self.executable_addresses

    def save_map_format(self, filename):
        """
        Guarda en formato .map (dirección,flag)
        flag = 1 si ejecutable, 0 si dato
        """
        all_addresses = self.executable_addresses | self.data_addresses

        with open(filename, "w") as f:
            for addr in sorted(all_addresses):
                flag = 1 if addr in self.executable_addresses else 0
                f.write(f"0x{addr:08X},{flag}\n")
