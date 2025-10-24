"""
Ejecutor de instrucciones de control de flujo
"""

from typing import Any, Dict

from src.cpu.core import Flags
from src.cpu.registers import RegisterFile
from src.cpu.stack_ops import StackOperations
from src.isa.isa import Opcodes


class ControlFlowExecutor:
    """Ejecuta instrucciones de control de flujo (JMP, JZ, CALL, RET, etc.)"""

    def __init__(self, registers: RegisterFile, stack_ops: StackOperations):
        """
        Inicializa el ejecutor de control de flujo

        Args:
            registers: Banco de registros
            stack_ops: Operaciones de pila
        """
        self.registers = registers
        self.stack_ops = stack_ops

    def execute(self, instruction: Dict[str, Any], cpu) -> bool:
        """
        Ejecuta una instrucción de control de flujo

        Args:
            instruction: Instrucción decodificada
            cpu: Referencia a la CPU (para modificar PC y leer flags)

        Returns:
            True para continuar ejecución
        """
        opcode = instruction["opcode"]
        imm32 = instruction["imm32"]  # Dirección de salto

        handlers = {
            Opcodes.JMP: self._execute_jmp,
            Opcodes.JZ: self._execute_jz,
            Opcodes.JNZ: self._execute_jnz,
            Opcodes.JC: self._execute_jc,
            Opcodes.JNC: self._execute_jnc,
            Opcodes.JS: self._execute_js,
            Opcodes.CALL: self._execute_call,
            Opcodes.RET: self._execute_ret,
        }

        handler = handlers.get(opcode)
        if handler:
            handler(imm32, cpu)

        return True

    def _execute_jmp(self, target: int, cpu):
        """JMP address - Salto incondicional"""
        cpu.pc = target

    def _execute_jz(self, target: int, cpu):
        """JZ address - Salto si Zero flag está activado"""
        if self._get_flag(cpu.flags, Flags.ZERO):
            cpu.pc = target

    def _execute_jnz(self, target: int, cpu):
        """JNZ address - Salto si Zero flag NO está activado"""
        if not self._get_flag(cpu.flags, Flags.ZERO):
            cpu.pc = target

    def _execute_jc(self, target: int, cpu):
        """JC address - Salto si Carry flag está activado"""
        if self._get_flag(cpu.flags, Flags.CARRY):
            cpu.pc = target

    def _execute_jnc(self, target: int, cpu):
        """JNC address - Salto si Carry flag NO está activado"""
        if not self._get_flag(cpu.flags, Flags.CARRY):
            cpu.pc = target

    def _execute_js(self, target: int, cpu):
        """JS address - Salto si Negative flag está activado"""
        if self._get_flag(cpu.flags, Flags.NEGATIVE):
            cpu.pc = target

    def _execute_call(self, target: int, cpu):
        """CALL address - Llamada a subrutina"""
        # Guardar dirección de retorno en la pila
        self.stack_ops.push(cpu.pc)
        # Saltar a la dirección objetivo
        cpu.pc = target

    def _execute_ret(self, target: int, cpu):
        """RET - Retorno de subrutina"""
        # Restaurar dirección de retorno desde la pila
        cpu.pc = self.stack_ops.pop()

    def _get_flag(self, flags: int, flag: Flags) -> bool:
        """
        Obtiene el estado de un flag

        Args:
            flags: Registro de flags (8 bits)
            flag: Flag específico a verificar

        Returns:
            True si el flag está activado
        """
        return bool(flags & (1 << flag))
