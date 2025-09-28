"""
Este archivo contiene pruebas unitarias adaptadas al formato
de instrucciones de 64 bits con campos RD, RS1, RS2, FUNC e IMM32.
"""

import unittest
import struct
import sys
import os

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cpu.cpu import (
    CPU, ALU, Decoder, Opcodes, AddressingMode, InstructionType,
    ALUOperation, Flags, create_sample_program
)


class TestInstructionDecoderNewFormat(unittest.TestCase):
    """Pruebas para el decodificador"""
    
    def setUp(self):
        self.decoder = Decoder()
    
    def test_encode_decode_r_type(self):
        """Prueba codificacion y decodificacion R-Type"""
        # ADD R2, R0, R1
        opcode = Opcodes.ADD
        rd = 2
        rs1 = 0
        rs2 = 1
        func = 0
        
        # Codificar
        encoded = self.decoder.encode_r_type(opcode, rd, rs1, rs2, func)
        
        # Decodificar
        decoded = self.decoder.decode(encoded)
        
        # Verificar
        self.assertEqual(decoded['opcode'], opcode)
        self.assertEqual(decoded['type'], InstructionType.R_TYPE)
        self.assertEqual(decoded['rd'], rd)
        self.assertEqual(decoded['rs1'], rs1)
        self.assertEqual(decoded['rs2'], rs2)
        self.assertEqual(decoded['func'], func)
        self.assertEqual(decoded['imm32'], 0)
    
    def test_encode_decode_i_type(self):
        """Prueba codificacion y decodificacion I-Type"""
        # MOV R1, #42
        opcode = Opcodes.MOV
        rd = 1
        rs1 = 0
        imm32 = 42
        func = 0
        
        # Codificar
        encoded = self.decoder.encode_i_type(opcode, rd, rs1, imm32, func)
        
        # Decodificar
        decoded = self.decoder.decode(encoded)
        
        # Verificar
        self.assertEqual(decoded['opcode'], opcode)
        self.assertEqual(decoded['type'], InstructionType.I_TYPE)
        self.assertEqual(decoded['rd'], rd)
        self.assertEqual(decoded['rs1'], rs1)
        self.assertEqual(decoded['imm32'], imm32)
        self.assertEqual(decoded['func'], func)
    
    def test_encode_decode_j_type(self):
        """Prueba codificacion y decodificacion J-Type"""
        # JMP #1000
        opcode = Opcodes.JMP
        address = 1000
        func = 0
        
        # Codificar
        encoded = self.decoder.encode_j_type(opcode, address, func)
        
        # Decodificar
        decoded = self.decoder.decode(encoded)
        
        # Verificar
        self.assertEqual(decoded['opcode'], opcode)
        self.assertEqual(decoded['type'], InstructionType.J_TYPE)
        self.assertEqual(decoded['imm32'], address)
        self.assertEqual(decoded['func'], func)
        self.assertEqual(decoded['rd'], 0)
        self.assertEqual(decoded['rs1'], 0)
        self.assertEqual(decoded['rs2'], 0)
    
    def test_encode_decode_s_type(self):
        """Prueba codificacion y decodificacion S-Type"""
        # HALT
        opcode = Opcodes.HALT
        func = 0
        
        # Codificar
        encoded = self.decoder.encode_s_type(opcode, func)
        
        # Decodificar
        decoded = self.decoder.decode(encoded)
        
        # Verificar
        self.assertEqual(decoded['opcode'], opcode)
        self.assertEqual(decoded['type'], InstructionType.S_TYPE)
        self.assertEqual(decoded['func'], func)
        self.assertEqual(decoded['imm32'], 0)
    
    def test_instruction_format(self):
        """Prueba formato de instruccion de 64 bits"""
        # Crear instruccion con valores especificos
        opcode = 0xFF
        rd = 0xF
        rs1 = 0xE
        rs2 = 0xD
        func = 0xABC
        imm32 = 0x12345678
        
        instruction = 0
        instruction |= (opcode & 0xFF) << 56
        instruction |= (rd & 0xF) << 52
        instruction |= (rs1 & 0xF) << 48
        instruction |= (rs2 & 0xF) << 44
        instruction |= (func & 0xFFF) << 32
        instruction |= (imm32 & 0xFFFFFFFF)
        
        # Verificar que cada campo este en la posicion correcta
        self.assertEqual((instruction >> 56) & 0xFF, 0xFF)      # Opcode
        self.assertEqual((instruction >> 52) & 0xF, 0xF)        # RD
        self.assertEqual((instruction >> 48) & 0xF, 0xE)        # RS1
        self.assertEqual((instruction >> 44) & 0xF, 0xD)        # RS2
        self.assertEqual((instruction >> 32) & 0xFFF, 0xABC)    # FUNC
        self.assertEqual(instruction & 0xFFFFFFFF, 0x12345678)  # IMM32


class TestCPUNewFormat(unittest.TestCase):
    """Pruebas para la CPU"""
    
    def setUp(self):
        self.cpu = CPU(memory_size=1024)
        self.decoder = Decoder()
    
    def test_mov_immediate_to_register(self):
        """Prueba MOV con inmediato a registro"""
        # MOV R0, #42
        instruction = self.decoder.encode_i_type(
            Opcodes.MOV, rd=0, rs1=0, imm32=42, func=0
        )
        decoded = self.cpu.decode(instruction)
        
        self.cpu.execute(decoded)
        
        self.assertEqual(self.cpu.registers[0], 42)
    
    def test_mov_register_to_register(self):
        """Prueba MOV de registro a registro"""
        # Configurar R1 = 100
        self.cpu.registers[1] = 100
        
        # MOV R0, R1
        instruction = self.decoder.encode_i_type(
            Opcodes.MOV, rd=0, rs1=1, imm32=0, func=1  # func=1 para registro a registro
        )
        decoded = self.cpu.decode(instruction)
        
        self.cpu.execute(decoded)
        
        self.assertEqual(self.cpu.registers[0], 100)
    
    def test_add_registers(self):
        """Prueba suma de registros"""
        # Configurar registros
        self.cpu.registers[0] = 10
        self.cpu.registers[1] = 20
        
        # ADD R2, R0, R1
        instruction = self.decoder.encode_r_type(
            Opcodes.ADD, rd=2, rs1=0, rs2=1, func=0
        )
        decoded = self.cpu.decode(instruction)
        
        self.cpu.execute(decoded)
        
        self.assertEqual(self.cpu.registers[2], 30)
        self.assertTrue(self.cpu.flags & (1 << Flags.POSITIVE))
    
    def test_stack_operations(self):
        """Prueba operaciones de pila"""
        # PUSH #100
        push_inst = self.decoder.encode_i_type(
            Opcodes.PUSH, rd=0, rs1=0, imm32=100, func=0
        )
        push_decoded = self.cpu.decode(push_inst)
        
        initial_sp = self.cpu.stack_pointer
        self.cpu.execute(push_decoded)
        
        # Verificar que el stack pointer decremento
        self.assertEqual(self.cpu.stack_pointer, initial_sp - 8)
        
        # POP R0
        pop_inst = self.decoder.encode_i_type(
            Opcodes.POP, rd=0, rs1=0, imm32=0, func=1
        )
        pop_decoded = self.cpu.decode(pop_inst)
        
        self.cpu.execute(pop_decoded)
        
        # Verificar que el valor se restauro y SP incremento
        self.assertEqual(self.cpu.registers[0], 100)
        self.assertEqual(self.cpu.stack_pointer, initial_sp)
    
    def test_jump_instruction(self):
        """Prueba instruccion de salto"""
        # JMP #200
        instruction = self.decoder.encode_j_type(Opcodes.JMP, 200, 0)
        decoded = self.cpu.decode(instruction)
        
        self.cpu.execute(decoded)
        
        self.assertEqual(self.cpu.pc, 200)
    
    def test_conditional_jump_zero(self):
        """Prueba salto condicional con flag zero"""
        # Establecer flag ZERO
        self.cpu._set_flag(Flags.ZERO, True)
        
        # JZ #100
        instruction = self.decoder.encode_j_type(Opcodes.JZ, 100, 0)
        decoded = self.cpu.decode(instruction)
        
        old_pc = self.cpu.pc
        self.cpu.execute(decoded)
        
        # Debe saltar porque ZERO esta activado
        self.assertEqual(self.cpu.pc, 100)
        
        # Probar cuando ZERO no esta activado
        self.cpu.pc = old_pc
        self.cpu._set_flag(Flags.ZERO, False)
        
        self.cpu.execute(decoded)
        
        # No debe saltar
        self.assertEqual(self.cpu.pc, old_pc)
    
    def test_call_return(self):
        """Prueba CALL y RET"""
        original_pc = self.cpu.pc = 100
        
        # CALL #500
        call_inst = self.decoder.encode_j_type(Opcodes.CALL, 500, 0)
        call_decoded = self.cpu.decode(call_inst)
        
        self.cpu.execute(call_decoded)
        
        # Verificar que PC cambio y se guardo la direccion de retorno
        self.assertEqual(self.cpu.pc, 500)
        
        # RET
        ret_inst = self.decoder.encode_s_type(Opcodes.RET, 0)
        ret_decoded = self.cpu.decode(ret_inst)
        
        self.cpu.execute(ret_decoded)
        
        # Debe regresar a la direccion original
        self.assertEqual(self.cpu.pc, original_pc)
    
    def test_halt_instruction(self):
        """Prueba instruccion HALT"""
        instruction = self.decoder.encode_s_type(Opcodes.HALT, 0)
        decoded = self.cpu.decode(instruction)
        
        result = self.cpu.execute(decoded)
        
        # HALT debe retornar False para detener la CPU
        self.assertFalse(result)
    
    def test_load_store_instructions(self):
        """Prueba instrucciones LOAD y STORE"""
        # Poner un valor en R0
        self.cpu.registers[0] = 0xDEADBEEF
        
        # STORE R0, #200 (almacenar contenido de R0 en direccion 200)
        # Para STORE: rd=direccion no usada, rs1=registro fuente, imm32=direccion
        store_inst = self.decoder.encode_i_type(
            Opcodes.STORE, rd=0, rs1=0, imm32=200, func=0  # func=0 para direccion absoluta
        )
        store_decoded = self.cpu.decode(store_inst)
        self.cpu.execute(store_decoded)
        
        # Limpiar R1
        self.cpu.registers[1] = 0
        
        # LOAD R1, #200 (cargar desde direccion 200 a R1)
        load_inst = self.decoder.encode_i_type(
            Opcodes.LOAD, rd=1, rs1=0, imm32=200, func=0  # func=0 para direccion absoluta
        )
        load_decoded = self.cpu.decode(load_inst)
        self.cpu.execute(load_decoded)
        
        # R1 debe tener el mismo valor que tenia R0
        self.assertEqual(self.cpu.registers[1], 0xDEADBEEF)
    
    def test_complete_program_execution(self):
        """Prueba ejecucion completa de programa"""
        program = create_sample_program()
        self.cpu.load_program(program)
        
        # Ejecutar programa completo
        self.cpu.run(max_cycles=10)  # Limitar ciclos para evitar bucles infinitos
        
        # Verificar resultados esperados
        # R0 debe tener 30 (10 + 20), R2 debe tener 30 (copiado de R0)
        self.assertEqual(self.cpu.registers[0], 30)  # R0 + R1
        self.assertEqual(self.cpu.registers[1], 20)
        self.assertEqual(self.cpu.registers[2], 30)  # Resultado copiado
        self.assertFalse(self.cpu.running)  # CPU debe estar detenida


class TestALUNewFormat(unittest.TestCase):
    """Pruebas para la ALU (sin cambios)"""
    
    def setUp(self):
        self.alu = ALU()
    
    def test_add_operation(self):
        """Prueba operacion de suma"""
        result, flags = self.alu.execute(ALUOperation.ADD, 10, 20)
        self.assertEqual(result, 30)
        self.assertTrue(flags & (1 << Flags.POSITIVE))
        self.assertFalse(flags & (1 << Flags.ZERO))
    
    def test_sub_operation(self):
        """Prueba operacion de resta"""
        result, flags = self.alu.execute(ALUOperation.SUB, 30, 10)
        self.assertEqual(result, 20)
        self.assertTrue(flags & (1 << Flags.POSITIVE))
    
    def test_zero_flag(self):
        """Prueba flag de cero"""
        result, flags = self.alu.execute(ALUOperation.SUB, 10, 10)
        self.assertEqual(result, 0)
        self.assertTrue(flags & (1 << Flags.ZERO))


if __name__ == '__main__':
    # Ejecutar solo las pruebas
    unittest.main(verbosity=2)