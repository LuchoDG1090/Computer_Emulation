"""
Ejecutor de instrucciones de pila
"""

from typing import Any, Dict

from src.cpu.registers import RegisterFile
from src.cpu.stack_ops import StackOperations
from src.isa.isa import Opcodes


class StackExecutor:
    """Ejecuta instrucciones de pila (PUSH, POP)"""

    def __init__(self, registers: RegisterFile, stack_ops: StackOperations):
        """
        Inicializa el ejecutor de pila

        Args:
            registers: Banco de registros
            stack_ops: Operaciones de pila
        """
        self.registers = registers
        self.stack_ops = stack_ops

    def execute(self, instruction: Dict[str, Any]) -> bool:
        """
        Ejecuta una instrucción de pila

        Args:
            instruction: Instrucción decodificada

        Returns:
            True para continuar ejecución
        """
        opcode = instruction["opcode"]

        if opcode == Opcodes.PUSH:
            self._execute_push(instruction)
        elif opcode == Opcodes.POP:
            self._execute_pop(instruction)

        return True

    def _execute_push(self, instruction: Dict[str, Any]):
        """
        PUSH Rs1 o PUSH #imm

        Args:
            instruction: Instrucción decodificada
        """
        rs1 = instruction["rs1"]
        imm32 = instruction["imm32"]
        func = instruction["func"]

        if func == 0:  # Inmediato
            value = imm32
        else:  # Registro
            value = self.registers[rs1]

        self.stack_ops.push(value)

    def _execute_pop(self, instruction: Dict[str, Any]):
        """
        POP Rd

        Args:
            instruction: Instrucción decodificada
        """
        rd = instruction["rd"]

        value = self.stack_ops.pop()
        self.registers[rd] = value
