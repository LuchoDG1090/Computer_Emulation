# src/memory/memory.py
import struct
from typing import Optional


class Memory:

    def __init__(self, size_bytes: int = 1024 * 1024):
        """
        Inicializa la memoria.
        :param size_bytes: tamaño total en bytes (default = 1 MiB).
        """
        self.size = size_bytes
        self.data = bytearray(size_bytes)

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
