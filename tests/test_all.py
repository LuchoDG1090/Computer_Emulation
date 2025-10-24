"""
Suite completa de tests para el emulador
Prueba todas las funcionalidades implementadas
"""

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.assembler.assembler import Assembler
from src.cpu.cpu import CPU
from src.isa.isa import Opcodes
from src.memory.loader import Loader


class TestAssembler:
    """Tests del ensamblador"""

    def test_compile_simple_program(self):
        """Compilar un programa simple"""
        code = """
        ORG 0x0
        MOVI R1, 42
        HALT
        """
        assembler = Assembler()
        binary = assembler.assemble(code)

        assert binary is not None
        lines = [l for l in binary.strip().split("\n") if l]
        assert len(lines) == 2

    def test_compile_with_labels(self):
        """Compilar programa con etiquetas"""
        code = """
        ORG 0x0
        inicio:
            MOVI R1, 10
            JMP inicio
        """
        assembler = Assembler()
        binary = assembler.assemble(code)

        assert binary is not None
        assert assembler.symbol_table.exists("inicio")

    def test_compile_with_data(self):
        """Compilar programa con directivas de datos"""
        code = """
        ORG 0x0
        MOVI R1, valor
        HALT
        ORG 0x100
        valor: DW 123
        """
        assembler = Assembler()
        binary = assembler.assemble(code)

        assert binary is not None
        assert assembler.symbol_table.exists("valor")

    def test_compile_with_string(self):
        """Compilar programa con strings"""
        code = """
        ORG 0x0
        HALT
        ORG 0x100
        mensaje: DB "Hola"
        """
        assembler = Assembler()
        binary = assembler.assemble(code)

        assert binary is not None


class TestCPUBasic:
    """Tests basicos de la CPU"""

    def test_alu_add(self):
        """Probar instruccion ADD"""
        cpu = CPU(memory_size=1024)
        cpu.registers[2] = 10
        cpu.registers[3] = 20

        instruction = (Opcodes.ADD << 56) | (1 << 52) | (2 << 48) | (3 << 44)
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.registers[1] == 30

    def test_alu_sub(self):
        """Probar instruccion SUB"""
        cpu = CPU(memory_size=1024)
        cpu.registers[2] = 50
        cpu.registers[3] = 20

        instruction = (Opcodes.SUB << 56) | (1 << 52) | (2 << 48) | (3 << 44)
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.registers[1] == 30

    def test_alu_mul(self):
        """Probar instruccion MUL"""
        cpu = CPU(memory_size=1024)
        cpu.registers[2] = 5
        cpu.registers[3] = 6

        instruction = (Opcodes.MUL << 56) | (1 << 52) | (2 << 48) | (3 << 44)
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.registers[1] == 30

    def test_alu_div(self):
        """Probar instruccion DIV"""
        cpu = CPU(memory_size=1024)
        cpu.registers[2] = 100
        cpu.registers[3] = 10

        instruction = (Opcodes.DIV << 56) | (1 << 52) | (2 << 48) | (3 << 44)
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.registers[1] == 10

    def test_movi_integer(self):
        """Probar MOVI con entero"""
        cpu = CPU(memory_size=1024)

        instruction = (Opcodes.MOVI << 56) | (1 << 52) | 100
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.registers[1] == 100

    def test_movi_negative(self):
        """Probar MOVI con numero negativo"""
        cpu = CPU(memory_size=1024)

        imm32 = (-50) & 0xFFFFFFFF
        instruction = (Opcodes.MOVI << 56) | (1 << 52) | imm32
        cpu.mem.write_word(0, instruction)
        cpu.step()

        result = cpu.registers[1]
        if result > 0x7FFFFFFFFFFFFFFF:
            result = result - (1 << 64)

        assert result == -50


class TestCPUMemory:
    """Tests de operaciones de memoria"""

    def test_load_store(self):
        """Probar LD y ST"""
        cpu = CPU(memory_size=2048)

        cpu.mem.write_word(0x100, 0xDEADBEEF)

        instruction = (Opcodes.LD << 56) | (1 << 52) | 0x100
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.registers[1] == 0xDEADBEEF

        cpu.pc = 8
        instruction = (Opcodes.ST << 56) | (1 << 52) | 0x200
        cpu.mem.write_word(8, instruction)
        cpu.step()

        assert cpu.mem.read_word(0x200) == 0xDEADBEEF

    def test_load_store_relative(self):
        """Probar LD/ST con direccionamiento relativo"""
        cpu = CPU(memory_size=2048)

        cpu.registers[2] = 0x100
        cpu.mem.write_word(0x108, 0xCAFEBABE)

        instruction = (Opcodes.LD << 56) | (1 << 52) | (2 << 48) | (1 << 32) | 8
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.registers[1] == 0xCAFEBABE


class TestCPUControlFlow:
    """Tests de control de flujo"""

    def test_jmp(self):
        """Probar JMP"""
        cpu = CPU(memory_size=1024)

        instruction = (Opcodes.JMP << 56) | 0x100
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.pc == 0x100

    def test_jz_taken(self):
        """Probar JZ cuando Z=1"""
        cpu = CPU(memory_size=1024)
        cpu.flags = 1 << 0  # Set Z flag

        instruction = (Opcodes.JZ << 56) | 0x100
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.pc == 0x100

    def test_jz_not_taken(self):
        """Probar JZ cuando Z=0"""
        cpu = CPU(memory_size=1024)
        cpu.flags = 0  # Clear Z flag

        instruction = (Opcodes.JZ << 56) | 0x100
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.pc == 8

    def test_call_ret(self):
        """Probar CALL y RET"""
        cpu = CPU(memory_size=2048)

        instruction = (Opcodes.CALL << 56) | 0x100
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert cpu.pc == 0x100

        instruction = Opcodes.RET << 56
        cpu.mem.write_word(0x100, instruction)
        cpu.step()

        assert cpu.pc == 8


class TestCPUFloatingPoint:
    """Tests de punto flotante"""

    def test_fadd(self):
        """Probar FADD"""
        cpu = CPU(memory_size=1024)

        import struct

        val1 = struct.unpack("Q", struct.pack("d", 3.5))[0]
        val2 = struct.unpack("Q", struct.pack("d", 2.5))[0]

        cpu.registers[2] = val1
        cpu.registers[3] = val2

        instruction = (Opcodes.FADD << 56) | (1 << 52) | (2 << 48) | (3 << 44)
        cpu.mem.write_word(0, instruction)
        cpu.step()

        result = struct.unpack("d", struct.pack("Q", cpu.registers[1]))[0]
        assert abs(result - 6.0) < 0.0001

    def test_fsub(self):
        """Probar FSUB"""
        cpu = CPU(memory_size=1024)

        import struct

        val1 = struct.unpack("Q", struct.pack("d", 10.5))[0]
        val2 = struct.unpack("Q", struct.pack("d", 3.5))[0]

        cpu.registers[2] = val1
        cpu.registers[3] = val2

        instruction = (Opcodes.FSUB << 56) | (1 << 52) | (2 << 48) | (3 << 44)
        cpu.mem.write_word(0, instruction)
        cpu.step()

        result = struct.unpack("d", struct.pack("Q", cpu.registers[1]))[0]
        assert abs(result - 7.0) < 0.0001


class TestCPUIO:
    """Tests de entrada/salida"""

    def test_output_int(self):
        """Probar salida de entero"""
        cpu = CPU(memory_size=1024)

        output = []
        cpu.io_ports.set_output_int_callback(lambda v: output.append(v))

        cpu.registers[1] = 42
        instruction = (Opcodes.OUT << 56) | (1 << 48) | 0xFFFF0008
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert output == [42]

    def test_output_char(self):
        """Probar salida de caracter"""
        cpu = CPU(memory_size=1024)

        output = []
        cpu.io_ports.set_output_char_callback(lambda ch: output.append(chr(ch)))

        cpu.registers[1] = ord("A")
        instruction = (Opcodes.OUT << 56) | (1 << 48) | 0xFFFF0000
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert output == ["A"]

    def test_output_string(self):
        """Probar salida de string"""
        cpu = CPU(memory_size=2048)

        test_str = "Hello"
        for i, ch in enumerate(test_str):
            cpu.mem.write_byte(0x100 + i, ord(ch))
        cpu.mem.write_byte(0x100 + len(test_str), 0)

        output = []
        cpu.io_ports.set_output_char_callback(lambda ch: output.append(chr(ch)))

        cpu.registers[1] = 0x100
        instruction = (Opcodes.OUTS << 56) | (1 << 52) | 0xFFFF0008
        cpu.mem.write_word(0, instruction)
        cpu.step()

        assert "".join(output) == test_str


class TestIntegration:
    """Tests de integracion completos"""

    def test_compile_and_execute(self):
        """Compilar y ejecutar un programa completo"""
        code = """
        ORG 0x0
        MOVI R1, 10
        MOVI R2, 20
        ADD R3, R1, R2
        OUT R3, 0xFFFF0008
        HALT
        """

        assembler = Assembler()
        binary = assembler.assemble(code)

        cpu = CPU(memory_size=2048)

        output = []
        cpu.io_ports.set_output_int_callback(lambda v: output.append(v))

        address = 0
        for line in binary.strip().split("\n"):
            if line:
                value = int(line, 2)
                cpu.mem.write_word(address, value)
                address += 8

        cpu.run(max_cycles=1000)

        assert output == [30]

    def test_compile_with_loader(self, tmp_path):
        """Compilar y cargar con el loader/linker"""
        code = """
        ORG 0x0
        MOVI R1, 5
        MOVI R2, 3
        MUL R3, R1, R2
        OUT R3, 0xFFFF0008
        HALT
        """

        asm_file = tmp_path / "test.asm"
        asm_file.write_text(code)

        bin_file = tmp_path / "test.bin"
        map_file = tmp_path / "test.map"

        assembler = Assembler()
        assembler.assemble_file(str(asm_file), str(bin_file), str(map_file))

        assert bin_file.exists()
        assert map_file.exists()

        cpu = CPU(memory_size=2048)

        output = []
        cpu.io_ports.set_output_int_callback(lambda v: output.append(v))

        Loader.cargar_programa(cpu, str(bin_file), str(map_file))

        cpu.run(max_cycles=1000)

        assert output == [15]

    def test_negative_numbers(self):
        """Probar manejo de numeros negativos"""
        code = """
        ORG 0x0
        MOVI R1, -10
        MOVI R2, 5
        ADD R3, R1, R2
        HALT
        """

        assembler = Assembler()
        binary = assembler.assemble(code)

        cpu = CPU(memory_size=2048)

        address = 0
        for line in binary.strip().split("\n"):
            if line:
                value = int(line, 2)
                cpu.mem.write_word(address, value)
                address += 8

        cpu.run(max_cycles=1000)

        result = cpu.registers[3]
        if result > 0x7FFFFFFFFFFFFFFF:
            result = result - (1 << 64)

        assert result == -5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
