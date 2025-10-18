"""
Ejecutor de instrucciones ALU
"""

from typing import Any, Dict

from src.cpu.core import ALU, ALUOperation
from src.cpu.registers import RegisterFile
from src.isa.isa import Opcodes


class ALUExecutor:
    """Ejecuta instrucciones aritméticas y lógicas"""

    def __init__(self, registers: RegisterFile, alu: ALU):
        """
        Inicializa el ejecutor ALU

        Args:
            registers: Banco de registros
            alu: Unidad aritmético-lógica
        """
        self.registers = registers
        self.alu = alu

        # Mapeo de opcodes a operaciones ALU
        self.opcode_to_alu_op = {
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

    def execute(self, instruction: Dict[str, Any], cpu) -> bool:
        """
        Ejecuta una instrucción ALU

        Args:
            instruction: Instrucción decodificada
            cpu: Referencia a la CPU (para actualizar flags)

        Returns:
            True para continuar ejecución
        """
        opcode = instruction["opcode"]
        rd = instruction["rd"]
        rs1 = instruction["rs1"]
        rs2 = instruction["rs2"]

        # Obtener operandos
        operand1 = self.registers[rs1]
        operand2 = self.registers[rs2] if self._requires_two_operands(opcode) else 0

        # Ejecutar operación ALU
        alu_operation = self.opcode_to_alu_op[opcode]
        result, flags = self.alu.execute(alu_operation, operand1, operand2)

        # Actualizar flags en CPU
        cpu.flags = flags

        # Guardar resultado (excepto CMP que solo afecta flags)
        if opcode != Opcodes.CMP:
            self.registers[rd] = result & 0xFFFFFFFFFFFFFFFF

        return True

    def _requires_two_operands(self, opcode: Opcodes) -> bool:
        """
        Verifica si la operación requiere dos operandos

        Args:
            opcode: Código de operación

        Returns:
            True si requiere dos operandos
        """
        single_operand_ops = {Opcodes.NOT}
        return opcode not in single_operand_ops
