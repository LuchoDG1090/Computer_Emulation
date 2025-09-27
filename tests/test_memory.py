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
        # Como tu Memory ya no recibe size_words, lo cambiamos a size_bytes
        self.mem = Memory(size_bytes=16)  # 16 bytes = 2 palabras de 64 bits
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
        # Escribir un byte completo (soporte oficial en Bus)
        self.bus.bus_write(0, 0xAB, 8)
        self.assertEqual(self.bus.bus_read(0, 8), 0xAB)

        # Escribir una palabra completa (64 bits)
        value = 0x1122334455667788
        self.bus.bus_write(0, value, 64)
        self.assertEqual(self.bus.bus_read(0, 64), value)

        # Escribir un bit (posición 0)
        self.bus.bus_write(1, 1, 1)
        self.assertEqual(self.bus.bus_read(1, 1), 1)

    def test_file_dump_and_load(self):
        # Escribir valores
        self.mem.write_byte(0, 0xAA)
        self.mem.write_byte(1, 0xBB)

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "mem_test.bin")

            # Volcar a archivo
            self.mem.dump_to_file(filename)

            # Cargar en nueva memoria
            mem2 = Memory(size_bytes=16)
            mem2.load_from_file(filename)

            self.assertEqual(mem2.read_byte(0), 0xAA)
            self.assertEqual(mem2.read_byte(1), 0xBB)


if __name__ == '__main__':
    unittest.main()
