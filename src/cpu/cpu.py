"""
CPU Emulator Module - M1 (Refactorizado)

Coordinador principal de la CPU - Solo lógica, sin interfaz.
"""

from typing import Any, Callable, Dict, Optional

from src.cpu.core import ALU
from src.cpu.decoder import Decoder
from src.cpu.execution.alu_executor import ALUExecutor
from src.cpu.execution.control_flow_executor import ControlFlowExecutor
from src.cpu.execution.data_transfer_executor import DataTransferExecutor
from src.cpu.execution.stack_executor import StackExecutor
from src.cpu.io_ports import IOPorts
from src.cpu.memory_ops import MemoryOperations
from src.cpu.registers import RegisterFile
from src.cpu.stack_ops import StackOperations
from src.isa.isa import Opcodes
from src.memory.memory import Memory


class CPU:
    """CPU de 64 bits - Arquitectura Von Neumann"""

    def __init__(self, memory_size: int = 65536, memory: Optional[Memory] = None):
        """
        Inicializa la CPU

        Args:
            memory_size: Tamaño de memoria en bytes (default 64KB)
            memory: Objeto Memory externo (opcional)
        """
        # Memoria
        self.mem: Memory = (
            memory if memory is not None else Memory(size_bytes=memory_size)
        )
        self.memory_size: int = self.mem.size
        self.memory: bytearray = self.mem.data  # Compatibilidad

        # Componentes
        self.registers = RegisterFile()
        self.alu = ALU()
        self.decoder = Decoder()
        self.memory_ops = MemoryOperations(self.mem)
        self.stack_ops = StackOperations(self.mem, self.memory_size)
        self.io_ports = IOPorts(self.mem, self.memory_size)

        # Ejecutores
        self.alu_executor = ALUExecutor(self.registers, self.alu)
        self.data_transfer_executor = DataTransferExecutor(
            self.registers, self.memory_ops, self.io_ports
        )
        self.control_flow_executor = ControlFlowExecutor(self.registers, self.stack_ops)
        self.stack_executor = StackExecutor(self.registers, self.stack_ops)

        # Registros especiales
        self.pc: int = 0
        self.ir: int = 0
        self.flags: int = 0

        # Estado
        self.running: bool = False
        self.cycle_count: int = 0
        self.step_mode: bool = False  # Modo paso a paso

        # Callback para pausas en step mode (la GUI lo usa)
        self.on_step_callback: Optional[Callable[[Dict], None]] = None

        # Mapa de ejecución
        self.exec_map: Optional[set[int]] = None
        self.segments: list[tuple[int, int, str]] = []
        self.current_program: Optional[str] = None
        self.occupied_words: set[int] = set()

    def reset(self):
        """Reinicia la CPU a su estado inicial"""
        self.pc = 0
        self.ir = 0
        self.flags = 0
        self.registers.reset()
        self.stack_ops.reset()
        self.mem.data[:] = b"\x00" * self.mem.size
        self.running = False
        self.cycle_count = 0
        self.step_mode = False
        self.exec_map = None
        self.segments = []
        self.current_program = None
        self.occupied_words = set()

    def load_program(self, program: bytes, start_address: int = 0):
        """Carga un programa en memoria"""
        if start_address + len(program) > self.mem.size:
            raise ValueError("Programa demasiado grande para la memoria")

        self.mem.data[start_address : start_address + len(program)] = program
        self.pc = start_address

    # === Ciclo Fetch-Decode-Execute ===

    def fetch(self) -> int:
        """Fase FETCH: Obtiene la instrucción"""
        if self.pc >= self.memory_size - 7:
            raise RuntimeError("Program Counter fuera de límites")

        if self.exec_map is not None and self.pc not in self.exec_map:
            try:
                next_exec = min(a for a in self.exec_map if a >= self.pc)
                self.pc = next_exec
            except ValueError:
                raise RuntimeError(
                    f"Intento de ejecutar dato/no ejecutable en 0x{self.pc:08X}"
                )

        instruction = self.mem.read_word(self.pc)
        self.ir = instruction
        self.pc += 8
        return instruction

    def decode(self, instruction: int) -> Dict[str, Any]:
        """Fase DECODE: Decodifica la instrucción"""
        return self.decoder.decode(instruction)

    def execute(self, decoded_instruction: Dict[str, Any]) -> bool:
        """Fase EXECUTE: Ejecuta la instrucción"""
        opcode = decoded_instruction["opcode"]

        if opcode in self._get_alu_opcodes():
            return self.alu_executor.execute(decoded_instruction, self)

        elif opcode in self._get_data_transfer_opcodes():
            return self.data_transfer_executor.execute(decoded_instruction, self)

        elif opcode in self._get_stack_opcodes():
            return self.stack_executor.execute(decoded_instruction)

        elif opcode in self._get_control_flow_opcodes():
            return self.control_flow_executor.execute(decoded_instruction, self)

        elif opcode == Opcodes.HALT:
            return False

        elif opcode == Opcodes.NOP:
            return True

        else:
            raise RuntimeError(f"Opcode no reconocido: {opcode}")

    # === Clasificación de Opcodes ===

    def _get_alu_opcodes(self):
        return {
            Opcodes.ADD,
            Opcodes.SUB,
            Opcodes.MUL,
            Opcodes.DIV,
            Opcodes.AND,
            Opcodes.OR,
            Opcodes.XOR,
            Opcodes.NOT,
            Opcodes.SHL,
            Opcodes.SHR,
            Opcodes.CMP,
        }

    def _get_data_transfer_opcodes(self):
        return {
            Opcodes.MOVI,
            Opcodes.LD,
            Opcodes.ST,
            Opcodes.OUT,
            Opcodes.ADDI,
            Opcodes.IN,
            Opcodes.CP,
            Opcodes.INS,
            Opcodes.OUTS,
        }

    def _get_stack_opcodes(self):
        return {Opcodes.PUSH, Opcodes.POP}

    def _get_control_flow_opcodes(self):
        return {
            Opcodes.JMP,
            Opcodes.JZ,
            Opcodes.JNZ,
            Opcodes.JC,
            Opcodes.JNC,
            Opcodes.JS,
            Opcodes.CALL,
            Opcodes.RET,
        }

    # === Ejecución ===

    def step(self) -> bool:
        """
        Ejecuta UN ciclo (fetch-decode-execute)

        Returns:
            True si debe continuar, False si debe detenerse
        """
        try:
            instruction = self.fetch()
            decoded = self.decode(instruction)
            should_continue = self.execute(decoded)
            self.cycle_count += 1

            # Si hay callback en step mode, notificar a la GUI
            if self.step_mode and self.on_step_callback:
                self.on_step_callback(self.get_state())

            return should_continue

        except Exception as e:
            raise RuntimeError(f"Error en ciclo CPU: {e}")

    def run(self, max_cycles: int = None):
        """
        Ejecuta la CPU continuamente

        Args:
            max_cycles: Máximo de ciclos (None = sin límite)
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

    def enable_step_mode(self, callback: Optional[Callable[[Dict], None]] = None):
        """
        Activa modo paso a paso

        Args:
            callback: Función que se llama después de cada step (opcional)
        """
        self.step_mode = True
        self.on_step_callback = callback

    def disable_step_mode(self):
        """Desactiva modo paso a paso"""
        self.step_mode = False
        self.on_step_callback = None

    def stop(self):
        """Detiene la ejecución"""
        self.running = False

    # === Estado ===

    def get_state(self) -> Dict[str, Any]:
        """Retorna el estado completo de la CPU"""
        return {
            "pc": self.pc,
            "ir": self.ir,
            "flags": self.flags,
            "registers": self.registers.get_all(),
            "stack_pointer": self.stack_ops.stack_pointer,
            "cycle_count": self.cycle_count,
            "running": self.running,
            "step_mode": self.step_mode,
        }
