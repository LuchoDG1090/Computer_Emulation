"""Generador de mapas de memoria"""


class MemoryMap:
    """Gestiona el mapa de memoria ejecutable"""

    def __init__(self):
        self.entries = {}
        self.order = []

    def _register(self, address, flag, index):
        """Registra una dirección asociada a un índice de palabra"""
        if index is None:
            raise ValueError(
                "Se requiere un índice de palabra para registrar en el mapa"
            )

        if index not in self.entries:
            self.entries[index] = {"address": address, "flag": flag}
            self.order.append(index)
        else:
            # Actualizar bandera si cambia (datos -> ejecutable)
            existing = self.entries[index]
            existing["address"] = address
            existing["flag"] = max(existing["flag"], flag)

    def mark_executable(self, address, index):
        """Marca una dirección como ejecutable"""
        self._register(address, 1, index)

    def mark_data(self, address, index):
        """Marca una dirección como datos"""
        self._register(address, 0, index)

    def is_executable(self, address):
        """Verifica si una dirección es ejecutable"""
        for entry in self.entries.values():
            if entry["address"] == address and entry["flag"] == 1:
                return True
        return False

    def save_map_format(self, filename):
        """
        Guarda en formato .map: índice, dirección original y flag
        flag = 1 si ejecutable, 0 si dato
        """
        with open(filename, "w") as f:
            for index in self.order:
                entry = self.entries[index]
                f.write(f"{index},0x{entry['address']:08X},{entry['flag']}\n")
