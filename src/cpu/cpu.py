"""
CPU Emulator Module - M1

Implementacion de CPU que sigue la arquitectura Von Neumann con:
- Tamaño de instrucciones: 64 bits
- Endianness: Little-endian
- Registros: PC, IR, MAR, MDR, Accumulator, Flag Register (8 bits), 16 registros de proposito general
- ALU con 40+ microinstrucciones basicas
- Conjunto de instrucciones: ALU, LD/ST, JMP, JZ/JNZ, CALL/RET, PUSH/POP, HALT

"""

import struct
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, IntEnum
from src.isa.isa import Opcodes, InstructionType, opcode_to_type
from src.memory.memory import Memory


# Banderas de la CPU
class Flags(IntEnum):
    """Flags del registro de estado (8 bits)"""
    ZERO = 0        # Bit 0: Resultado es cero
    CARRY = 1       # Bit 1: Acarreo
    NEGATIVE = 2    # Bit 2: Resultado negativo
    POSITIVE = 3    # Bit 3: Resultado positivo
    OVERFLOW = 4    # Bit 4: Desbordamiento
    INTERRUPT = 5   # Bit 5: Interrupcion
    # Bits 6-7: Reservados

class AddressingMode(IntEnum):
    """Modos de direccionamiento"""
    IMMEDIATE = 0   # Inmediato
    REGISTER = 1    # Registro
    DIRECT = 2      # Directo
    INDIRECT = 3    # Indirecto
    INDEXED = 4     # Indexado


class ALUOperation(IntEnum):
    """Operaciones de la ALU"""
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3
    AND = 4
    OR = 5
    XOR = 6
    NOT = 7
    SHL = 8
    SHR = 9
    CMP = 10
    INC = 11
    DEC = 12
    NEG = 13


class CPU:
    """
    Clase principal de la CPU que implementa una arquitectura Von Neumann de 64 bits
    """
    
    def __init__(self, memory_size: int = 65536, memory: Optional[Memory] = None):
        """
        Inicializa la CPU con los registros y componentes necesarios
        
        Args:
            memory_size: Tamaño de la memoria en bytes (por defecto 64KB)
        """
        # Registros principales
        self.pc: int = 0                    # Program Counter (64 bits)
        self.ir: int = 0                    # Instruction Register (64 bits)
        self.mar: int = 0                   # Memory Address Register
        self.mdr: int = 0                   # Memory Data Register
        self.accumulator: int = 0           # Acumulador
        self.flags: int = 0                 # Flag Register (8 bits)
        
        # Registros de proposito general (R0-R15)
        self.registers: List[int] = [0] * 16
        
        # Memoria principal (usar Memory externo)
        self.mem: Memory = memory if memory is not None else Memory(size_bytes=memory_size)
        self.memory_size: int = self.mem.size
        
        # Compatibilidad: exponer el buffer como 'memory'
        self.memory: bytearray = self.mem.data
        
        # Pila y stack pointer (iniciar en el tope de memoria)
        self.stack_pointer: int = self.mem.size
        
        # Estado de la CPU
        self.running: bool = False
        self.cycle_count: int = 0
        
        # Inicializar componentes
        self.alu = ALU()
        self.decoder = InstructionDecoder()

        # Salidas MMIO simples
        self.MMIO_CONSOLE_CHAR = 0xFFFF0000  # escribe byte (ASCII) a consola
        self.MMIO_CONSOLE_INT  = 0xFFFF0008  # imprime entero en consola
        self.io_ports = {
            1: self._console_port_write_char,
            2: self._console_port_write_int,
        }

        # Puertos de entrada
        self.MMIO_CONSOLE_IN_CHAR = 0xFFFF0010  # lee un caracter (ASCII) desde consola
        self.MMIO_CONSOLE_IN_INT  = 0xFFFF0018  # lee un entero desde consola
        self.io_ports_in = {
            1: self._console_port_read_char,   # puerto 1: leer ASCII
            2: self._console_port_read_int,    # puerto 2: leer entero
        }

        # Mapa de direcciones ejecutables (None => no verificar)
        self.exec_map: Optional[set[int]] = None
    
    def reset(self):
        """Reinicia la CPU a su estado inicial"""
        self.pc = 0
        self.ir = 0
        self.mar = 0
        self.mdr = 0
        self.accumulator = 0
        self.flags = 0
        self.registers = [0] * 16
        self.mem.data[:] = b"\x00" * self.mem.size
        self.memory_size = self.mem.size
        self.memory = self.mem.data
        self.stack_pointer = self.mem.size
        self.running = False
        self.cycle_count = 0
    
    def load_program(self, program: bytes, start_address: int = 0):
        """
        Carga un programa en memoria
        
        Args:
            program: Programa en bytes
            start_address: Direccion de inicio en memoria
        """
        if start_address + len(program) > self.mem.size:
            raise ValueError("Programa demasiado grande para la memoria")
        
        self.mem.data[start_address:start_address + len(program)] = program
        self.pc = start_address
    
    def fetch(self) -> int:
        """
        Fase FETCH: Obtiene la instruccion de memoria
        """
        if self.pc >= self.memory_size - 7:
            raise RuntimeError("Program Counter fuera de limites")
        if self.exec_map is not None and self.pc not in self.exec_map:
            try:
                next_exec = min(a for a in self.exec_map if a >= self.pc)
                self.pc = next_exec
            except ValueError:
                raise RuntimeError(f"Intento de ejecutar dato/no ejecutable en 0x{self.pc:08X}")
        # Leer instrucción de 64 bits desde Memory
        instruction = self.mem.read_word(self.pc)
        self.ir = instruction
        self.pc += 8
        return instruction
    
    def decode(self, instruction: int) -> Dict[str, Any]:
        """
        Fase DECODE: Decodifica la instruccion
        
        Args:
            instruction: Instruccion de 64 bits
            
        Returns:
            Diccionario con los campos decodificados
        """
        return self.decoder.decode(instruction)
    
    def execute(self, decoded_instruction: Dict[str, Any]) -> bool:
        """
        Fase EXECUTE: Ejecuta la instruccion decodificada
        
        Args:
            decoded_instruction: Instruccion decodificada
            
        Returns:
            True si la CPU debe continuar ejecutando, False si debe detenerse
        """
        opcode = decoded_instruction['opcode']
        
        # Instrucciones ALU
        if opcode in [Opcodes.ADD, Opcodes.SUB, Opcodes.MUL, Opcodes.DIV,
                      Opcodes.AND, Opcodes.OR, Opcodes.XOR, Opcodes.NOT,
                      Opcodes.SHL, Opcodes.SHR, Opcodes.CMP]:
            return self._execute_alu_instruction(decoded_instruction)
        
        # Instrucciones de transferencia de datos
        elif opcode in [Opcodes.MOVI, Opcodes.LD, Opcodes.ST, 
                        Opcodes.OUT, Opcodes.ADDI, Opcodes.IN, Opcodes.CP]:
            return self._execute_data_transfer(decoded_instruction)
        
        # Instrucciones de pila
        elif opcode in [Opcodes.PUSH, Opcodes.POP]:
            return self._execute_stack_instruction(decoded_instruction)
        
        # Instrucciones de control de flujo
        elif opcode in [Opcodes.JMP, Opcodes.JZ, Opcodes.JNZ, Opcodes.JC, 
                        Opcodes.JNC, Opcodes.JS, Opcodes.CALL, Opcodes.RET]:
            return self._execute_control_flow(decoded_instruction)

        # Instrucciones de sistema
        elif opcode == Opcodes.HALT:
            return False
        elif opcode == Opcodes.NOP:
            return True
        
        else:
            raise RuntimeError(f"Opcode no reconocido: {opcode}")
    
    def step(self) -> bool:
        """
        Ejecuta un ciclo completo de la CPU (fetch-decode-execute)
        
        Returns:
            True si la CPU debe continuar, False si debe detenerse
        """
        try:
            # Fase FETCH
            instruction = self.fetch()
            
            # Fase DECODE
            decoded = self.decode(instruction)
            
            # Fase EXECUTE
            should_continue = self.execute(decoded)
            
            self.cycle_count += 1
            return should_continue
        
        except Exception as e:
            print(f"Error en ciclo CPU: {e}")
            return False
    
    def run(self, max_cycles: int = None):
        """
        Ejecuta la CPU hasta que se detenga o alcance el maximo de ciclos
        
        Args:
            max_cycles: Maximo numero de ciclos a ejecutar (None = sin limite)
        """
        self.running = True
        cycles = 0
        
        while self.running:
            if max_cycles and cycles >= max_cycles:
                break
            
            should_continue = self.step()
            if not should_continue:
                self.running = False
                break
            
            cycles += 1
        
        print(f"CPU detenida despues de {cycles} ciclos")
    
    def _execute_alu_instruction(self, instruction: Dict[str, Any]) -> bool:
        """Ejecuta instrucciones de la ALU (R-Type)"""
        opcode = instruction['opcode']
        rd = instruction['rd']
        rs1 = instruction['rs1']
        rs2 = instruction['rs2']
        func = instruction['func']
        
        # Obtener valores de los registros fuente
        operand1 = self.registers[rs1]
        
        # Para operaciones que requieren dos operandos
        if opcode in [Opcodes.ADD, Opcodes.SUB, Opcodes.MUL, Opcodes.DIV, 
                      Opcodes.AND, Opcodes.OR, Opcodes.XOR, Opcodes.SHL, 
                      Opcodes.SHR, Opcodes.CMP]:
            operand2 = self.registers[rs2]
        else:  # NOT solo requiere un operando
            operand2 = 0
        
        # Mapear opcode a operacion ALU
        alu_op_map = {
            Opcodes.ADD: ALUOperation.ADD,
            Opcodes.SUB: ALUOperation.SUB,
            Opcodes.MUL: ALUOperation.MUL,
            Opcodes.DIV: ALUOperation.DIV,
            Opcodes.AND: ALUOperation.AND,
            Opcodes.OR: ALUOperation.OR,
            Opcodes.XOR: ALUOperation.XOR,
            Opcodes.NOT: ALUOperation.NOT,
            Opcodes.SHL: ALUOperation.SHL,
            Opcodes.SHR: ALUOperation.SHR,
            Opcodes.CMP: ALUOperation.CMP,
        }
        
        alu_operation = alu_op_map[opcode]
        result, flags = self.alu.execute(alu_operation, operand1, operand2)
        
        # Actualizar flags
        self.flags = flags
        
        # Almacenar resultado en registro destino (excepto para CMP)
        if opcode != Opcodes.CMP:
            self.registers[rd] = result & 0xFFFFFFFFFFFFFFFF  # Mantener 64 bits
        
        return True
    
    def _execute_data_transfer(self, instruction: Dict[str, Any]) -> bool:
        """Ejecuta instrucciones de transferencia de datos (I-Type)"""
        opcode = instruction['opcode']
        rd = instruction['rd']
        rs1 = instruction['rs1']
        imm32 = instruction['imm32']
        func = instruction['func']
        
        if opcode == Opcodes.MOVI:
            # MOVI puede ser MOVI Rd, Rs1 (registro a registro) o MOVI Rd, #imm (inmediato)
            if func == 0:  # Inmediato
                self.registers[rd] = imm32
            else:  # Registro a registro (func = 1)
                self.registers[rd] = self.registers[rs1]
        
        elif opcode == Opcodes.LD:
            # LD Rd, Rs1 + offset o LD Rd, #address
            if func == 0:  # Direccion absoluta
                address = imm32
            else:  # Offset desde registro base
                address = self.registers[rs1] + self._sign_extend_32(imm32)
            
            value = self._read_memory_64(address)
            self.registers[rd] = value
        
        elif opcode == Opcodes.ST:
            # ST Rs1, Rd + offset o ST Rs1, #address
            if func == 0:  # Direccion absoluta
                address = imm32
            else:  # Offset desde registro base
                address = self.registers[rd] + self._sign_extend_32(imm32)
            
            value = self.registers[rs1]
            self._write_memory_64(address, value)
        
        elif opcode == Opcodes.OUT:
            # OUT: escribe valor de registro a MMIO (func=0) o puerto (func=1)
            # Acepta ambas codificaciones: registro en RD (ensamblador) o RS1 (encoder manual)
            src_reg_val = self.registers[rs1] if rs1 != 0 else self.registers[rd]
            self._io_out(src_reg_val, imm32, func)

        elif opcode == Opcodes.IN:
            # IN Rd, imm32: lee de MMIO (func=0) o puerto (func=1) y guarda en Rd  <-- NUEVO
            value = self._io_in(imm32, func)
            self.registers[rd] = value & 0xFFFFFFFFFFFFFFFF

        elif opcode == Opcodes.ADDI:
            # ADDI Rd, Rs1, #imm32  => Rd = Rs1 + imm32
            operand1 = self.registers[rs1]
            operand2 = self._sign_extend_32(imm32)
            result, flags = self.alu.execute(ALUOperation.ADD, operand1, operand2)
            self.registers[rd] = result & 0xFFFFFFFFFFFFFFFF  # Mantener 64 bits
            self.flags = flags

        elif opcode == Opcodes.CP:
            # CP Rd, Rs1  => copia registro a registro (no afecta flags)
            self.registers[rd] = self.registers[rs1] & 0xFFFFFFFFFFFFFFFF

        return True
    
    def _io_out(self, value: int, target: int, func: int):
        """Salida a MMIO o puertos."""
        if func == 1:
            # salida a puerto numerico
            handler = self.io_ports.get(target)
            if handler:
                handler(value)
            else:
                # puerto desconocido: traza simple
                print(f"[OUT:port {target}] {value}")
        else:
            # salida a direccion MMIO absoluta
            if target == self.MMIO_CONSOLE_CHAR:
                self._console_port_write_char(value)
            elif target == self.MMIO_CONSOLE_INT:
                self._console_port_write_int(value)
            else:
                # MMIO generico: escribir como memoria (si aplica)
                # proteccion: no escribir fuera de memoria
                if 0 <= target <= (self.memory_size - 8):
                    self._write_memory_64(target, value)
                else:
                    # direccion MMIO fuera de RAM: solo traza
                    print(f"[OUT:mmio 0x{target:08X}] {value}")

    def _io_in(self, source: int, func: int) -> int:
        """Entrada desde MMIO o puertos. Retorna un entero de 64 bits."""
        if func == 1:
            # entrada desde puerto numerico
            handler = self.io_ports_in.get(source)
            if handler:
                return handler()
            print(f"[IN:port {source}] sin handler, devuelve 0")
            return 0
        else:
            # entrada desde direccion MMIO absoluta
            if source == self.MMIO_CONSOLE_IN_CHAR:
                return self._console_port_read_char()
            elif source == self.MMIO_CONSOLE_IN_INT:
                return self._console_port_read_int()
            else:
                # MMIO generico: leer como memoria si esta en rango
                if 0 <= source <= (self.memory_size - 8):
                    return self._read_memory_64(source)
                print(f"[IN:mmio 0x{source:08X}] sin handler, devuelve 0")
                return 0

    def _console_port_write_char(self, value: int):
        """Escribe el byte menos significativo como caracter."""
        ch = value & 0xFF
        try:
            print(chr(ch), end="")
        except Exception:
            print(f"[CONS:char] 0x{ch:02X}", end="")

    def _console_port_write_int(self, value: int):
        """Imprime el valor como entero decimal."""
        print(int(value & 0xFFFFFFFFFFFFFFFF))

    def _console_port_read_char(self) -> int:
        """Lee un caracter de la consola y retorna su codigo ASCII (LSB)."""
        try:
            import sys
            ch = sys.stdin.read(1)
            if ch:
                return ord(ch[0]) & 0xFF
        except Exception:
            pass
        return 0

    def _console_port_read_int(self) -> int:
        """Lee un entero desde consola. Acepta decimal/hex (0x...)."""
        try:
            s = input()
            return int(s, 0) & 0xFFFFFFFFFFFFFFFF
        except Exception:
            return 0

    def _execute_stack_instruction(self, instruction: Dict[str, Any]) -> bool:
        """Ejecuta instrucciones de pila (I-Type)"""
        opcode = instruction['opcode']
        rd = instruction['rd']
        rs1 = instruction['rs1']
        imm32 = instruction['imm32']
        func = instruction['func']
        
        if opcode == Opcodes.PUSH:
            # PUSH Rs1 (registro) o PUSH #imm (inmediato)
            if func == 0:  # Inmediato
                value = imm32
            else:  # Registro
                value = self.registers[rs1]
            self._push(value)
        
        elif opcode == Opcodes.POP:
            # POP Rd (siempre a registro)
            value = self._pop()
            self.registers[rd] = value
        
        return True
    
    def _execute_control_flow(self, instruction: Dict[str, Any]) -> bool:
        """Ejecuta instrucciones de control de flujo (J-Type)"""
        opcode = instruction['opcode']
        imm32 = instruction['imm32']  # Direccion de salto
        func = instruction['func']
        
        if opcode == Opcodes.JMP:
            self.pc = imm32
        
        elif opcode == Opcodes.JZ:
            if self._get_flag(Flags.ZERO):
                self.pc = imm32
        
        elif opcode == Opcodes.JNZ:
            if not self._get_flag(Flags.ZERO):
                self.pc = imm32
        
        elif opcode == Opcodes.JC:
            if self._get_flag(Flags.CARRY):
                self.pc = imm32
        
        elif opcode == Opcodes.JNC:
            if not self._get_flag(Flags.CARRY):
                self.pc = imm32
        
        elif opcode == Opcodes.JS:
            if self._get_flag(Flags.NEGATIVE):
                self.pc = imm32

        elif opcode == Opcodes.CALL:
            self._push(self.pc)  # Guardar direccion de retorno
            self.pc = imm32
        
        elif opcode == Opcodes.RET:
            self.pc = self._pop()  # Restaurar direccion de retorno
        
        return True
    
    def _sign_extend_32(self, value: int) -> int:
        """Extiende el signo de un valor de 32 bits a 64 bits"""
        if value & 0x80000000:  # Si el bit de signo esta activado
            return value | 0xFFFFFFFF00000000  # Extender con 1s
        else:
            return value & 0xFFFFFFFF  # Mantener positivo
    
    def _read_memory_64(self, address: int) -> int:
        """Lee un valor de 64 bits desde memoria (Memory)"""
        return self.mem.read_word(address)
    
    def _write_memory_64(self, address: int, value: int):
        """Escribe un valor de 64 bits en memoria (Memory)"""
        self.mem.write_word(address, value & 0xFFFFFFFFFFFFFFFF)
    
    def _push(self, value: int):
        """Empuja un valor a la pila (crecimiento hacia abajo en bloques de 8 bytes)"""
        if self.stack_pointer < 8:
            raise RuntimeError("Stack overflow")
        self.stack_pointer -= 8
        self._write_memory_64(self.stack_pointer, value)

    def _pop(self) -> int:
        """Saca un valor de la pila"""
        if self.stack_pointer >= self.mem.size:
            raise RuntimeError("Stack underflow")
        value = self._read_memory_64(self.stack_pointer)
        self.stack_pointer += 8
        return value
    
    def _get_flag(self, flag: Flags) -> bool:
        """Obtiene el estado de un flag"""
        return bool(self.flags & (1 << flag))
    
    def _set_flag(self, flag: Flags, value: bool):
        """Establece el estado de un flag"""
        if value:
            self.flags |= (1 << flag)
        else:
            self.flags &= ~(1 << flag)
    
    def get_state(self) -> Dict[str, Any]:
        """Retorna el estado actual de la CPU"""
        return {
            'pc': self.pc,
            'ir': self.ir,
            'mar': self.mar,
            'mdr': self.mdr,
            'accumulator': self.accumulator,
            'flags': self.flags,
            'registers': self.registers.copy(),
            'stack_pointer': self.stack_pointer,
            'cycle_count': self.cycle_count,
            'running': self.running
        }
    
    def print_state(self):
        """Imprime el estado actual de la CPU"""
        state = self.get_state()
        print("=== ESTADO DE LA CPU ===")
        print(f"PC: 0x{state['pc']:016X}")
        print(f"IR: 0x{state['ir']:016X}")
        print(f"Accumulator: 0x{state['accumulator']:016X}")
        print(f"Flags: 0b{state['flags']:08b}")
        print(f"Stack Pointer: 0x{state['stack_pointer']:016X}")
        print(f"Cycles: {state['cycle_count']}")
        print(f"Running: {state['running']}")
        
        print("\nRegistros:")
        for i, reg in enumerate(state['registers']):
            print(f"R{i}: 0x{reg:016X}")


class ALU:
    """Unidad Aritmetico-Logica"""
    
    def execute(self, operation: ALUOperation, operand1: int, operand2: int = 0) -> Tuple[int, int]:
        """
        Ejecuta una operacion en la ALU
        
        Args:
            operation: Operacion a realizar
            operand1: Primer operando
            operand2: Segundo operando (opcional)
            
        Returns:
            Tupla (resultado, flags)
        """
        flags = 0
        
        # Asegurar que los operandos sean de 64 bits con signo
        operand1 = self._to_signed_64(operand1)
        operand2 = self._to_signed_64(operand2)
        
        if operation == ALUOperation.ADD:
            result = operand1 + operand2
        elif operation == ALUOperation.SUB:
            result = operand1 - operand2
        elif operation == ALUOperation.MUL:
            result = operand1 * operand2
        elif operation == ALUOperation.DIV:
            if operand2 == 0:
                raise RuntimeError("Division por cero")
            result = operand1 // operand2
        elif operation == ALUOperation.AND:
            result = operand1 & operand2
        elif operation == ALUOperation.OR:
            result = operand1 | operand2
        elif operation == ALUOperation.XOR:
            result = operand1 ^ operand2
        elif operation == ALUOperation.NOT:
            result = ~operand1
        elif operation == ALUOperation.SHL:
            result = operand1 << (operand2 & 63)  # Limitar shift a 63 bits
        elif operation == ALUOperation.SHR:
            result = operand1 >> (operand2 & 63)
        elif operation == ALUOperation.CMP:
            result = operand1 - operand2
        elif operation == ALUOperation.INC:
            result = operand1 + 1
        elif operation == ALUOperation.DEC:
            result = operand1 - 1
        elif operation == ALUOperation.NEG:
            result = -operand1
        else:
            raise ValueError(f"Operacion ALU no reconocida: {operation}")
        
        # Calcular flags
        flags = self._calculate_flags(result, operand1, operand2, operation)
        
        # Convertir resultado a 64 bits sin signo
        result = result & 0xFFFFFFFFFFFFFFFF
        
        return result, flags
    
    def _to_signed_64(self, value: int) -> int:
        """Convierte un valor a entero con signo de 64 bits"""
        value = value & 0xFFFFFFFFFFFFFFFF
        if value & 0x8000000000000000:
            return value - 0x10000000000000000
        return value
    
    def _calculate_flags(self, result: int, op1: int, op2: int, operation: ALUOperation) -> int:
        """Calcula los flags basado en el resultado y operacion"""
        flags = 0
        
        # Zero flag
        if result == 0:
            flags |= (1 << Flags.ZERO)
        
        # Negative flag
        if result < 0:
            flags |= (1 << Flags.NEGATIVE)
        else:
            flags |= (1 << Flags.POSITIVE)
        
        # Carry flag (para operaciones aritmeticas)
        if operation in [ALUOperation.ADD, ALUOperation.SUB]:
            if operation == ALUOperation.ADD:
                if (op1 > 0 and op2 > 0 and result < 0) or \
                   (op1 < 0 and op2 < 0 and result > 0):
                    flags |= (1 << Flags.CARRY)
            
        # Overflow flag
        if operation in [ALUOperation.ADD, ALUOperation.SUB, ALUOperation.MUL]:
            if result > 0x7FFFFFFFFFFFFFFF or result < -0x8000000000000000:
                flags |= (1 << Flags.OVERFLOW)
        
        return flags


class InstructionDecoder:
    """Decodificador de instrucciones de 64 bits"""
    
    def decode(self, instruction: int) -> Dict[str, Any]:
        """
        Decodifica una instruccion de 64 bits
        
        Formato de instruccion (64 bits):
        [63-56] Opcode (8 bits)
        [55-52] RD - Registro destino (4 bits) 
        [51-48] RS1 - Registro fuente 1 (4 bits)
        [47-44] RS2 - Registro fuente 2 (4 bits)
        [43-32] FUNC - Campo de funcion o modificador (12 bits)
        [31-0]  IMM32 - Campo inmediato/direccion (32 bits)
        
        Args:
            instruction: Instruccion de 64 bits
            
        Returns:
            Diccionario con campos decodificados
        """
        opcode = (instruction >> 56) & 0xFF
        rd = (instruction >> 52) & 0xF
        rs1 = (instruction >> 48) & 0xF
        rs2 = (instruction >> 44) & 0xF
        func = (instruction >> 32) & 0xFFF
        imm32 = instruction & 0xFFFFFFFF
        
        # Determinar tipo de instruccion
        inst_type = opcode_to_type.get(opcode, InstructionType.S_TYPE)
        
        return {
            'opcode': opcode,
            'type': inst_type,
            'rd': rd,
            'rs1': rs1,
            'rs2': rs2,
            'func': func,
            'imm32': imm32
        }


def create_sample_program() -> bytes:
    """
    Crea un programa de ejemplo para probar la CPU 
    
    Returns:
        Programa en bytes
    """
    decoder = InstructionDecoder()
    instructions = []
    
    # MOVI R0, #10 (inmediato) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOVI, rd=0, rs1=0, imm32=10, func=0  # func=0 para inmediato
    ))
    
    # MOVI R1, #20 - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOVI, rd=1, rs1=0, imm32=20, func=0
    ))
    
    # ADD R0, R0, R1 (R0 = R0 + R1) - R-Type
    instructions.append(decoder.encode_r_type(
        Opcodes.ADD, rd=0, rs1=0, rs2=1, func=0
    ))
    
    # MOVI R2, R0 (guardar resultado) - I-Type con func=1 para registro
    instructions.append(decoder.encode_i_type(
        Opcodes.MOVI, rd=2, rs1=0, imm32=0, func=1  # func=1 para registro a registro
    ))
    
    # HALT - S-Type
    instructions.append(decoder.encode_s_type(Opcodes.HALT))
    
    # Convertir a bytes
    program = bytearray()
    for inst in instructions:
        program.extend(struct.pack('<Q', inst))
    
    return bytes(program)


# Funcion principal para pruebas
if __name__ == "__main__":
    # Crear CPU
    cpu = CPU()
    
    # Cargar programa de ejemplo
    program = create_sample_program()
    cpu.load_program(program)
    
    print("=== PROGRAMA DE EJEMPLO CARGADO ===")
    print("Instrucciones:")
    print("1. MOVI R0, #10")
    print("2. MOVI R1, #20") 
    print("3. ADD R0, R1")
    print("4. MOVI R2, R0")
    print("5. HALT")
    print()
    
    # Mostrar estado inicial
    print("Estado inicial:")
    cpu.print_state()
    print()
    
    # Ejecutar programa
    print("=== EJECUTANDO PROGRAMA ===")
    cpu.run()
    
    # Mostrar estado final
    print("\nEstado final:")
    cpu.print_state()
    
    print(f"\nResultado esperado: R2 = 30 (10 + 20)")
    print(f"Resultado obtenido: R2 = {cpu.registers[2]}")
