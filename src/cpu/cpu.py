"""
CPU Emulator Module - M1

Implementacion de CPU que sigue la arquitectura Von Neumann con:
- Tamaño de instrucciones: 64 bits
- Endianness: Little-endian
- Registros: PC, IR, MAR, MDR, Accumulator, Flag Register (8 bits), 16 registros de proposito general
- ALU con 40+ microinstrucciones basicas
- Conjunto de instrucciones: ALU, LD/ST, JMP, JZ/JNZ, CALL/RET, PUSH/POP, HALT

"""

from typing import Dict, List, Optional, Any
from src.isa.isa import Opcodes
from src.memory.memory import Memory
from src.cpu.core import ALU, ALUOperation, Flags
from src.cpu.decoder import Decoder
import src.user_interface.logging.logger as logger
from src.user_interface.cli import messages
from src.user_interface.cli.table_formater import Table
from src.user_interface.cli import color

logger_handler = logger.configurar_logger()

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
        self.decoder = Decoder()

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
    
    def __get_cpu_status(self):
        logger_handler.info("Se ha solicitado el estado actual de los registros del pc")
        return {
            "program counter / instruction pointer": str(self.pc),
            "instruction register": str(self.ir),
            "flag register(bin)": str(bin(self.flags)),
            "falg register(dec)": str(self.flags)
        }
    
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
            if max_cycles and cycles >= max_cycles: break
            
            should_continue = self.step()
            if not should_continue:
                self.running = False
                break
            
            cycles += 1
        
        print(f"CPU detenida despues de {cycles} ciclos")
    
    def run_cycles(self, max_cycles: int = None):
        self.running = True
        cycles = 0

        while self.running:
            if max_cycles and cycles >= max_cycles: break
            try:
                step = input("Para ejecutar la siguiente instrucción ingrese step, para salir ingrese q >>").strip().lower()
                if step not in ("q", "step"): raise EOFError
            except KeyboardInterrupt:
                print("\n")
                print(color.Color.ROJO)
                print("Para salir ingrese q")
                print(color.Color.RESET_COLOR)
                logger_handler.exception("Para salir el usuario debe ingresar q, no secuencias de escape")
            except EOFError:
                print("\n")
                print(color.Color.ROJO)
                print("Entrada de usuario no es correcta")
                print(color.Color.RESET_COLOR)
                logger_handler.exception("El valor ingresado por el usuario no es correcto")
            else:
                if step == "step":
                    should_continue = self.step()
                    estado_cpu = self.__get_cpu_status()
                    col, row = messages.Messages.get_terminal_size()
                    tabla_estado = Table(col, row, "Estado de la máquina")
                    tabla_estado.add_encabezado(["registro", "Valor"])
                    for k,v in estado_cpu.items():
                        tabla_estado.add_fila([k, v])
                    tabla_estado.print_table()
                    if not should_continue:
                        self.running = False
                        break
                elif step == "q":
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
            # IN Rd, ...
            # Extended subop: parse a line of integers into memory
            subop = (func >> 1) & 0x7
            sep_chr = (func >> 4) & 0xFF
            if subop == 1:
                base = self.registers[rs1]
                count = imm32 & 0xFFFFFFFF
                try:
                    line = input()
                except Exception:
                    line = ""
                # Default separator: ASCII from func (e.g., space=32). Fallback to whitespace split.
                parts = line.split(chr(sep_chr)) if sep_chr else line.split()
                for i in range(min(count, len(parts))):
                    try:
                        val = int(parts[i], 0)
                    except Exception:
                        val = 0
                    addr = base + i * 8
                    if 0 <= addr <= (self.memory_size - 8):
                        self._write_memory_64(addr, val)
                # Return number of parsed items in Rd
                self.registers[rd] = min(count, len(parts))
            else:
                # IN Rd, imm32: lee de MMIO (func=0) o puerto (func=1)
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
        # Decode extended OUT sub-operations using FUNC12 bits
        # Layout:
        #   bit 0   : 0 = MMIO mode (default), 1 = PORT mode
        #   bits 3:1: subop (0 = normal), 1 = print int array with separator
        #   bits 11:4: separator ASCII (0..255)
        mode_port = func & 1
        subop = (func >> 1) & 0x7
        sep_chr = (func >> 4) & 0xFF

        # Extended sub-operation: print array of integers with separator
        if subop == 1:
            base_addr = value            # base pointer to array of 64-bit words
            count = target & 0xFFFFFFFF  # number of elements to print
            # Clamp count to a reasonable upper bound to avoid runaway
            if count < 0:
                count = 0
            if count > 1_000_000:
                count = 1_000_000
            for i in range(count):
                addr = base_addr + i * 8
                if not (0 <= addr <= (self.memory_size - 8)):
                    break
                val = self._read_memory_64(addr)
                # print integer without newline
                self._print_int_no_newline(val)
                # print separator between numbers (not after last)
                if i != count - 1 and sep_chr:
                    self._console_port_write_char(sep_chr)
            return

        # Extended sub-operation: print single integer without newline
        if subop == 2:
            self._print_int_no_newline(value)
            return

        if mode_port == 1:
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

    def _print_int_no_newline(self, value: int):
        """Imprime el entero sin salto de línea (para salidas formateadas)."""
        try:
            print(int(value & 0xFFFFFFFFFFFFFFFF), end="")
        except Exception:
            # Fallback textual
            s = str(int(value & 0xFFFFFFFFFFFFFFFF))
            for ch in s:
                self._console_port_write_char(ord(ch))

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
