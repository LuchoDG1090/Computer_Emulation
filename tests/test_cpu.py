"""Test completo de la CPU refactorizada"""

import logging
import sys
from pathlib import Path

# Deshabilitar logging para evitar bugs
logging.disable(logging.CRITICAL)

# Configurar codificación UTF-8 para Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Agregar el directorio raíz al path para que las importaciones funcionen
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.assembler.assembler import Assembler
from src.cpu.cpu import CPU
from src.isa.isa import Opcodes


def test_basic_alu():
    """Prueba instrucciones ALU"""
    print("=== Test ALU ===")
    cpu = CPU(memory_size=1024)

    # Programa: ADD R1, R2, R3
    opcode = Opcodes.ADD << 56
    rd = 1 << 52
    rs1 = 2 << 48
    rs2 = 3 << 44
    instruction = opcode | rd | rs1 | rs2

    # Cargar valores en registros
    cpu.registers[2] = 10
    cpu.registers[3] = 20

    # Cargar instrucción en memoria
    cpu.mem.write_word(0, instruction)

    # Ejecutar
    cpu.step()

    # Verificar resultado
    assert cpu.registers[1] == 30, f"Esperado 30, obtenido {cpu.registers[1]}"
    print(f"✓ ADD: R1 = {cpu.registers[1]} (correcto)")
    print()


def test_movi():
    """Prueba MOVI"""
    print("=== Test MOVI ===")
    cpu = CPU(memory_size=1024)

    # MOVI R1, #100
    opcode = Opcodes.MOVI << 56
    rd = 1 << 52
    imm32 = 100
    func = 0  # Inmediato
    instruction = opcode | rd | (func << 32) | imm32

    cpu.mem.write_word(0, instruction)
    cpu.step()

    assert cpu.registers[1] == 100
    print(f"✓ MOVI: R1 = {cpu.registers[1]} (correcto)")
    print()


def test_load_store():
    """Prueba LD/ST"""
    print("=== Test LD/ST ===")
    cpu = CPU(memory_size=1024)

    # Escribir valor en memoria
    cpu.mem.write_word(0x100, 0xDEADBEEF)

    # LD R1, 0x100
    opcode = Opcodes.LD << 56
    rd = 1 << 52
    imm32 = 0x100
    func = 0  # Dirección absoluta
    instruction = opcode | rd | (func << 32) | imm32

    cpu.mem.write_word(0, instruction)
    cpu.step()

    assert cpu.registers[1] == 0xDEADBEEF
    print(f"✓ LD: R1 = 0x{cpu.registers[1]:X} (correcto)")

    # ST R1, 0x200
    cpu.pc = 8
    opcode = Opcodes.ST << 56
    rd = 1 << 52  # Corregido: ST usa rd, no rs1
    imm32 = 0x200
    instruction = opcode | rd | imm32

    cpu.mem.write_word(8, instruction)
    cpu.step()

    stored_value = cpu.mem.read_word(0x200)
    assert stored_value == 0xDEADBEEF
    print(f"✓ ST: Memoria[0x200] = 0x{stored_value:X} (correcto)")
    print()


def test_jump():
    """Prueba JMP"""
    print("=== Test JMP ===")
    cpu = CPU(memory_size=1024)

    # JMP 0x100
    opcode = Opcodes.JMP << 56
    imm32 = 0x100
    instruction = opcode | imm32

    cpu.mem.write_word(0, instruction)
    cpu.step()

    assert cpu.pc == 0x100
    print(f"✓ JMP: PC = 0x{cpu.pc:X} (correcto)")
    print()


def test_output():
    """Prueba OUT con callback"""
    print("=== Test OUT ===")
    cpu = CPU(memory_size=1024)

    output = []

    def callback(value):
        output.append(value)

    cpu.io_ports.set_output_int_callback(callback)

    # MOVI R1, 42
    opcode = Opcodes.MOVI << 56
    rd = 1 << 52
    imm32 = 42
    instruction = opcode | rd | imm32
    cpu.mem.write_word(0, instruction)

    # OUT R1, 0xFFFF0008
    cpu.pc = 0
    cpu.step()  # MOVI

    opcode = Opcodes.OUT << 56
    rs1 = 1 << 48
    imm32 = 0xFFFF0008
    instruction = opcode | rs1 | imm32
    cpu.mem.write_word(8, instruction)

    cpu.step()  # OUT

    assert output == [42]
    print(f"✓ OUT: Salida = {output} (correcto)")
    print()


def test_program():
    """Prueba un programa completo"""
    print("=== Test Programa Completo ===")
    cpu = CPU(memory_size=1024)

    output = []
    cpu.io_ports.set_output_int_callback(lambda v: output.append(v))

    # Programa: suma 5 + 10 y muestra resultado
    instructions = []

    # MOVI R1, 5
    instructions.append((Opcodes.MOVI << 56) | (1 << 52) | 5)

    # MOVI R2, 10
    instructions.append((Opcodes.MOVI << 56) | (2 << 52) | 10)

    # ADD R3, R1, R2
    instructions.append((Opcodes.ADD << 56) | (3 << 52) | (1 << 48) | (2 << 44))

    # OUT R3, 0xFFFF0008
    instructions.append((Opcodes.OUT << 56) | (3 << 48) | 0xFFFF0008)

    # HALT
    instructions.append(Opcodes.HALT << 56)

    # Cargar programa
    for i, inst in enumerate(instructions):
        cpu.mem.write_word(i * 8, inst)

    # Ejecutar
    cpu.run()

    assert output == [15]
    print(f"✓ Programa: 5 + 10 = {output[0]} (correcto)")
    print(f"✓ Ciclos ejecutados: {cpu.cycle_count}")
    print()


def test_with_assembler():
    """Test con ensamblador real"""
    print("=== Test con Ensamblador ===")

    # Código ensamblador
    codigo = """
ORG 0x0
    MOVI R1, 10
    MOVI R2, 20
    ADD R3, R1, R2
    OUT R3, 0xFFFF0008
    HALT
"""

    # Ensamblar
    assembler = Assembler()
    binario = assembler.assemble(codigo)

    # Convertir binario a palabras y cargar en memoria
    cpu = CPU()

    address = 0
    for linea in binario.strip().split("\n"):
        if linea:
            valor = int(linea, 2)
            cpu.mem.write_word(address, valor)
            address += 8

    # Configurar salida
    output = []
    cpu.io_ports.set_output_int_callback(lambda v: output.append(v))

    # Ejecutar
    cpu.run()

    assert output == [30]
    print(f"✓ Resultado: {output[0]} (correcto)")
    print(f"✓ Ciclos: {cpu.cycle_count}")
    print()


def test_strings():
    """Test de instrucciones de strings (INS/OUTS)"""
    print("=== Test Strings (OUTS) ===")

    cpu = CPU(memory_size=2048)

    # Escribir string en memoria manualmente
    test_string = "Hola Mundo!"
    for i, ch in enumerate(test_string):
        cpu.mem.write_byte(0x100 + i, ord(ch))
    cpu.mem.write_byte(0x100 + len(test_string), 0)  # Null terminator

    # OUTS R1, 0xFFFF0008
    cpu.registers[1] = 0x100  # Dirección del string

    opcode = Opcodes.OUTS << 56
    rd = 1 << 52
    imm32 = 0xFFFF0008
    instruction = opcode | rd | imm32

    cpu.mem.write_word(0, instruction)

    # Configurar callback
    output = []
    cpu.io_ports.set_output_char_callback(lambda ch: output.append(chr(ch)))

    cpu.step()

    resultado = "".join(output)
    assert resultado == test_string
    print(f"✓ String impreso: '{resultado}' (correcto)")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DE LA CPU REFACTORIZADA")
    print("=" * 60)
    print()

    try:
        test_basic_alu()
        test_movi()
        test_load_store()
        test_jump()
        test_output()
        test_program()
        test_with_assembler()
        test_strings()

        print("=" * 60)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ FALLO EN PRUEBA: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
