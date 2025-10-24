"""
Módulo de operaciones de memoria para la CPU
"""

from src.memory.memory import Memory


class MemoryOperations:
    """Maneja operaciones de lectura/escritura de memoria para la CPU"""

    def __init__(self, memory: Memory):
        """
        Inicializa operaciones de memoria

        Args:
            memory: Objeto Memory
        """
        self.mem = memory

    def read_word(self, address: int) -> int:
        """
        Lee una palabra de 64 bits desde memoria

        Args:
            address: Dirección de memoria (debe estar alineada a 8 bytes)

        Returns:
            Valor de 64 bits
        """
        if address < 0 or address > self.mem.size - 8:
            raise ValueError(
                f"Dirección de lectura fuera de rango: 0x{address:08X} "
                f"(memoria: 0-0x{self.mem.size:08X})"
            )

        return self.mem.read_word(address)

    def write_word(self, address: int, value: int):
        """
        Escribe una palabra de 64 bits en memoria

        Args:
            address: Dirección de memoria (debe estar alineada a 8 bytes)
            value: Valor de 64 bits a escribir
        """
        if address < 0 or address > self.mem.size - 8:
            raise ValueError(
                f"Dirección de escritura fuera de rango: 0x{address:08X} "
                f"(memoria: 0-0x{self.mem.size:08X})"
            )

        # Asegurar que el valor cabe en 64 bits
        self.mem.write_word(address, value & 0xFFFFFFFFFFFFFFFF)

    def read_byte(self, address: int) -> int:
        """
        Lee un byte desde memoria

        Args:
            address: Dirección de memoria

        Returns:
            Valor de 8 bits
        """
        if address < 0 or address >= self.mem.size:
            raise ValueError(f"Dirección fuera de rango: 0x{address:08X}")

        return self.mem.read_byte(address)

    def write_byte(self, address: int, value: int):
        """
        Escribe un byte en memoria

        Args:
            address: Dirección de memoria
            value: Valor de 8 bits a escribir
        """
        if address < 0 or address >= self.mem.size:
            raise ValueError(f"Dirección fuera de rango: 0x{address:08X}")

        self.mem.write_byte(address, value & 0xFF)

    def read_half_word(self, address: int) -> int:
        """
        Lee media palabra (16 bits) desde memoria

        Args:
            address: Dirección de memoria

        Returns:
            Valor de 16 bits
        """
        if address < 0 or address > self.mem.size - 2:
            raise ValueError(f"Dirección fuera de rango: 0x{address:08X}")

        return self.mem.read_half_word(address)

    def write_half_word(self, address: int, value: int):
        """
        Escribe media palabra (16 bits) en memoria

        Args:
            address: Dirección de memoria
            value: Valor de 16 bits a escribir
        """
        if address < 0 or address > self.mem.size - 2:
            raise ValueError(f"Dirección fuera de rango: 0x{address:08X}")

        self.mem.write_half_word(address, value & 0xFFFF)

    def read_double_word(self, address: int) -> int:
        """
        Lee doble palabra (32 bits) desde memoria

        Args:
            address: Dirección de memoria

        Returns:
            Valor de 32 bits
        """
        if address < 0 or address > self.mem.size - 4:
            raise ValueError(f"Dirección fuera de rango: 0x{address:08X}")

        return self.mem.read_double_word(address)

    def write_double_word(self, address: int, value: int):
        """
        Escribe doble palabra (32 bits) en memoria

        Args:
            address: Dirección de memoria
            value: Valor de 32 bits a escribir
        """
        if address < 0 or address > self.mem.size - 4:
            raise ValueError(f"Dirección fuera de rango: 0x{address:08X}")

        self.mem.write_double_word(address, value & 0xFFFFFFFF)

    def sign_extend_32(self, value: int) -> int:
        """
        Extiende el signo de un valor de 32 bits a 64 bits

        Args:
            value: Valor de 32 bits

        Returns:
            Valor de 64 bits con signo extendido
        """
        if value & 0x80000000:  # Si el bit de signo está activado
            return value | 0xFFFFFFFF00000000
        else:
            return value & 0xFFFFFFFF

    def is_valid_address(self, address: int, size: int = 8) -> bool:
        """
        Verifica si una dirección es válida

        Args:
            address: Dirección a verificar
            size: Tamaño del acceso en bytes (default 8 para palabra)

        Returns:
            True si la dirección es válida
        """
        return 0 <= address <= (self.mem.size - size)
