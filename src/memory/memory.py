# src/memory/memory.py
import struct
from typing import Optional
import src.user_interface.logging.logger as logger

logger_handler = logger.configurar_logger()

class Memory:

    def __init__(self, size_bytes: Optional[int] = None, size_words: Optional[int] = None):
        """
        Inicializa la memoria.
        :param size_bytes: tamaño en bytes.
        :param size_words: tamaño en palabras de 64 bits.
        """
        if size_words is not None:
            self.size = size_words * 8  # 1 palabra = 8 bytes
        elif size_bytes is not None:
            self.size = size_bytes
        else:
            self.size = 1024 * 1024  # default = 1 MiB
        logger_handler.info(f"Inicialización de memoria ram con tamaño {self.size}")
        self.data = bytearray(self.size)

    # ---------------------------
    #  ACCESO POR BYTE
    # ---------------------------
    def read_byte(self, addr: int) -> int:
        self._check_addr(addr)
        return self.data[addr]

    def write_byte(self, addr: int, value: int):
        self._check_addr(addr)
        self.data[addr] = value & 0xFF

    # ---------------------------
    #  ACCESO POR PALABRA (64 bits)
    # ---------------------------
    def read_word(self, addr: int) -> int:
        self._check_addr(addr, 8)
        return struct.unpack_from("<Q", self.data, addr)[0]  # Little-endian

    def write_word(self, addr: int, value: int):
        self._check_addr(addr, 8)
        struct.pack_into("<Q", self.data, addr, value & 0xFFFFFFFFFFFFFFFF)

    # ---------------------------
    #  ACCESO POR BIT
    # ---------------------------
    def read_bit(self, addr: int, bit_index: int) -> int:
        """
        Lee un bit específico en un byte.
        :param addr: dirección base del byte
        :param bit_index: índice (0 = LSB, 7 = MSB)
        """
        self._check_addr(addr)
        if not 0 <= bit_index < 8:
            raise ValueError("bit_index debe estar entre 0 y 7")
        byte_val = self.data[addr]
        return (byte_val >> bit_index) & 1

    def write_bit(self, addr: int, bit_index: int, value: int):
        self._check_addr(addr)
        if not 0 <= bit_index < 8:
            raise ValueError("bit_index debe estar entre 0 y 7")
        if value not in (0, 1):
            raise ValueError("El valor del bit debe ser 0 o 1")
        if value == 1:
            self.data[addr] |= (1 << bit_index)
        else:
            self.data[addr] &= ~(1 << bit_index)

    # ---------------------------
    #  CARGA Y VOLCADO A ARCHIVO
    # ---------------------------
    def load_from_file(self, filename: str):
        with open(filename, "rb") as f:
            content = f.read()
            n = min(len(content), self.size)
            self.data[:n] = content[:n]

    def dump_to_file(self, filename: str):
        with open(filename, "wb") as f:
            f.write(self.data)

    # ---------------------------
    #  HELPERS
    # ---------------------------
    def _check_addr(self, addr: int, size: int = 1):
        if addr < 0 or addr + size > self.size:
            raise ValueError(f"Dirección {addr} fuera de rango (0 - {self.size - 1})")

# src/memory/memory.py (continuación)

class Bus:
    """
    Bus lógico que conecta CPU y Memoria.
    Ofrece métodos bus_read y bus_write a nivel de bits.
    """

    def __init__(self, memory: Memory):
        self.memory = memory

    def bus_read(self, addr: int, nbits: int = 64) -> int:
        if nbits == 1:
            return self.memory.read_bit(addr, 0)
        elif nbits == 4:  # nibble
            byte_val = self.memory.read_byte(addr)
            return byte_val & 0x0F
        elif nbits % 8 == 0:  # múltiplos de 8 bits
            nbytes = nbits // 8
            self.memory._check_addr(addr, nbytes)
            return int.from_bytes(self.memory.data[addr:addr+nbytes], "little")
        else:
            raise ValueError("nbits soportados: 1, 4, múltiplos de 8")

    def bus_write(self, addr: int, value: int, nbits: int = 64):
        if nbits == 1:
            self.memory.write_bit(addr, 0, value)
        elif nbits == 4:  # nibble
            orig = self.memory.read_byte(addr)
            new_val = (orig & 0xF0) | (value & 0x0F)
            self.memory.write_byte(addr, new_val)
        elif nbits % 8 == 0:  # múltiplos de 8 bits
            nbytes = nbits // 8
            self.memory._check_addr(addr, nbytes)
            self.memory.data[addr:addr+nbytes] = value.to_bytes(nbytes, "little")
        else:
            raise ValueError("nbits soportados: 1, 4, múltiplos de 8")
