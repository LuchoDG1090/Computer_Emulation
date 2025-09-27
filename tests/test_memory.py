"""
Este archivo contiene pruebas unitarias para el módulo de Memoria y Bus.
Se valida acceso bit a bit, byte, palabra (64 bits), operaciones de bus,
y persistencia en archivos binarios.
"""

import unittest
import os
import tempfile

# Añadir el directorio src 
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory.memory import Memory, Bus


class TestMemory(unittest.TestCase):

    def setUp(self):
        self.mem = Memory(size_words=2)  # 2 palabras de 64 bits = 16 bytes
        self.bus = Bus(self.mem)

    def test_bit_read_write(self):
        # Escribir un bit en dirección 0, bit 3
        self.mem.write_bit(0, 3, 1)
        self.assertEqual(self.mem.read_bit(0, 3), 1)

        # Cambiarlo a 0
        self.mem.write_bit(0, 3, 0)
        self.assertEqual(self.mem.read_bit(0, 3), 0)

    def test_byte_read_write(self):
        # Escribir un byte
        self.mem.write_byte(0, 0xAB)
        self.assertEqual(self.mem.read_byte(0), 0xAB)

        # Cambiarlo
        self.mem.write_byte(0, 0xFF)
        self.assertEqual(self.mem.read_byte(0), 0xFF)

    def test_word_read_write(self):
        value = 0x1122334455667788
        self.mem.write_word(0, value)
        self.assertEqual(self.mem.read_word(0), value)

    def test_bus_read_write(self):
        # Escribir con bus_write
        self.bus.bus_write(0, 0b1010, 4)  # 4 bits
        self.assertEqual(self.bus.bus_read(0, 4), 0b1010)

        # Escribir un byte completo
        self.bus.bus_write(1, 0xFF, 8)
        self.assertEqual(self.bus.bus_read(1, 8), 0xFF)

    def test_file_dump_and_load(self):
        # Escribir valores
        self.mem.write_byte(0, 0xAA)
        self.mem.write_byte(1, 0xBB)

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "mem_test.bin")

            # Volcar a archivo
            self.mem.dump_to_binfile(filename)

            # Cargar en nueva memoria
            mem2 = Memory(size_words=2)
            mem2.load_from_binfile(filename)

            self.assertEqual(mem2.read_byte(0), 0xAA)
            self.assertEqual(mem2.read_byte(1), 0xBB)


if __name__ == '__main__':
    unittest.main()
