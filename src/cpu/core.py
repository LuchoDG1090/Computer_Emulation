import struct
from enum import IntEnum
from typing import Tuple

import src.user_interface.logging.logger as logger

logger_handler = logger.configurar_logger()


# Banderas de la CPU
class Flags(IntEnum):
    """Flags del registro de estado (8 bits)"""

    ZERO = 0  # Bit 0: Resultado es cero
    CARRY = 1  # Bit 1: Acarreo
    NEGATIVE = 2  # Bit 2: Resultado negativo
    POSITIVE = 3  # Bit 3: Resultado positivo
    OVERFLOW = 4  # Bit 4: Desbordamiento
    INTERRUPT = 5  # Bit 5: Interrupcion
    # Bits 6-7: Reservados


class AddressingMode(IntEnum):
    """Modos de direccionamiento"""

    IMMEDIATE = 0  # Inmediato
    REGISTER = 1  # Registro
    DIRECT = 2  # Directo
    INDIRECT = 3  # Indirecto
    INDEXED = 4  # Indexado


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


class ALU:
    """Unidad Aritmetico-Logica"""

    def execute(
        self, operation: ALUOperation, operand1: int, operand2: int = 0
    ) -> Tuple[int, int]:
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
            logger_handler.info(
                f"Desarrollo de la operación suma entre: {operand1} y {operand2} con resultado {result}"
            )
        elif operation == ALUOperation.SUB:
            result = operand1 - operand2
            logger_handler.info(
                f"Desarrollo de la operación resta entre {operand1} y {operand2} con resultado {result}"
            )
        elif operation == ALUOperation.MUL:
            result = operand1 * operand2
            logger_handler.info(
                f"Desarrollo de la operación multiplicación entre {operand1} y {operand2} con resultado {result}"
            )
        elif operation == ALUOperation.DIV:
            if operand2 == 0:
                logger_handler.error("Se intentó desarrollar una división por cero")
                raise RuntimeError("Division por cero")
            result = operand1 // operand2
            logger_handler.info(
                f"Desarrollo de la operación división entre {operand1} y {operand2} con resultado {result}"
            )
        elif operation == ALUOperation.AND:
            result = operand1 & operand2
            logger_handler.info(
                f"Desarrollo de la operación AND entre {operand1} y {operand2} con resultado {result}"
            )
        elif operation == ALUOperation.OR:
            result = operand1 | operand2
            logger_handler.info(
                f"Desarrollo de la operación OR entre {operand1} y {operand2} con resultado {result}"
            )
        elif operation == ALUOperation.XOR:
            result = operand1 ^ operand2
            logger_handler.info(
                f"Desarrollo de la operación XOR - or exclusivo entre {operand1} y {operand2} con resultado {result}"
            )
        elif operation == ALUOperation.NOT:
            result = ~operand1
            logger_handler.info(f"Desarrollo de la operación negación para {operand1}")
        elif operation == ALUOperation.SHL:
            result = operand1 << (operand2 & 63)  # Limitar shift a 63 bits
            logger_handler.info(
                f"Desarrollo de la operación shift left para {operand1}"
            )
        elif operation == ALUOperation.SHR:
            result = operand1 >> (operand2 & 63)
            logger_handler.info(
                f"Desarrollo de la operación shift right para {operand1}"
            )
        elif operation == ALUOperation.CMP:
            result = operand1 - operand2
            logger_handler.info(
                f"Desarrollo de la operación comparación para {operand1} y {operand2}"
            )
        elif operation == ALUOperation.INC:
            result = operand1 + 1
            logger_handler.info(
                f"Desarrollo de la operación incremento para {operand1}"
            )
        elif operation == ALUOperation.DEC:
            result = operand1 - 1
            logger_handler.info(
                f"Desarrollo de la operación decremento para {operand1}"
            )
        elif operation == ALUOperation.NEG:
            result = -operand1
        else:
            logger_handler.error(f"Operación de ALU no reconocida: {operation}")
            raise ValueError(f"Operacion ALU no reconocida: {operation}")

        # Calcular flags
        flags = self._calculate_flags(result, operand1, operand2, operation)
        logger_handler.info(f"Estado de la ALU por medio del flag register: {flags}")

        # Convertir resultado a 64 bits sin signo
        result = result & 0xFFFFFFFFFFFFFFFF

        return result, flags

    def _to_signed_64(self, value: int) -> int:
        """Convierte un valor a entero con signo de 64 bits"""
        value = value & 0xFFFFFFFFFFFFFFFF
        if value & 0x8000000000000000:
            return value - 0x10000000000000000
        return value

    def _calculate_flags(
        self, result: int, op1: int, op2: int, operation: ALUOperation
    ) -> int:
        """Calcula los flags basado en el resultado y operacion"""
        flags = 0

        # Zero flag
        if result == 0:
            flags |= 1 << Flags.ZERO

        # Negative flag
        if result < 0:
            flags |= 1 << Flags.NEGATIVE
        else:
            flags |= 1 << Flags.POSITIVE

        # Carry flag (para operaciones aritmeticas)
        if operation in [ALUOperation.ADD, ALUOperation.SUB]:
            if operation == ALUOperation.ADD:
                if (op1 > 0 and op2 > 0 and result < 0) or (
                    op1 < 0 and op2 < 0 and result > 0
                ):
                    flags |= 1 << Flags.CARRY

        # Overflow flag
        if operation in [ALUOperation.ADD, ALUOperation.SUB, ALUOperation.MUL]:
            if result > 0x7FFFFFFFFFFFFFFF or result < -0x8000000000000000:
                flags |= 1 << Flags.OVERFLOW

        return flags


class FloatALU:
    """Unidad Aritmética para operaciones de punto flotante IEEE 754"""

    def execute(self, operation: str, operand1: int, operand2: int) -> Tuple[int, int]:
        """
        Ejecuta una operación flotante

        Args:
            operation: 'FADD', 'FSUB', 'FMUL', 'FDIV'
            operand1: Primer operando (64 bits, interpretado como double)
            operand2: Segundo operando (64 bits, interpretado como double)

        Returns:
            Tupla (resultado_como_int_64bits, flags)
        """
        # Convertir de representación entera a float
        f1 = self.int_to_float(operand1)
        f2 = self.int_to_float(operand2)

        # Realizar operación
        if operation == "FADD":
            result_float = f1 + f2
        elif operation == "FSUB":
            result_float = f1 - f2
        elif operation == "FMUL":
            result_float = f1 * f2
        elif operation == "FDIV":
            if f2 == 0.0:
                # División por cero: resultado IEEE 754 es inf
                result_float = float("inf") if f1 >= 0 else float("-inf")
            else:
                result_float = f1 / f2
        else:
            raise ValueError(f"Operación flotante no reconocida: {operation}")

        # Convertir resultado de vuelta a int de 64 bits
        result_int = self.float_to_int(result_float)

        # Calcular flags
        flags = self._calculate_float_flags(result_float)

        logger_handler.info(f"FloatALU: {operation} {f1} y {f2} = {result_float}")

        return result_int, flags

    def int_to_float(self, value: int) -> float:
        """
        Convierte un entero de 64 bits a float (IEEE 754 double precision)

        Args:
            value: Entero de 64 bits (representación binaria de un double)

        Returns:
            float: Valor en punto flotante
        """
        # Asegurar que sea de 64 bits
        value = value & 0xFFFFFFFFFFFFFFFF
        # Usar struct para interpretar los bits como double
        return struct.unpack("d", struct.pack("Q", value))[0]

    def float_to_int(self, value: float) -> int:
        """
        Convierte un float a su representación entera de 64 bits (IEEE 754)

        Args:
            value: Valor en punto flotante

        Returns:
            int: Representación de 64 bits del float
        """
        # Usar struct para obtener la representación binaria
        return struct.unpack("Q", struct.pack("d", value))[0]

    def _calculate_float_flags(self, result: float) -> int:
        """Calcula flags para resultado flotante"""
        flags = 0

        if result == 0.0:
            flags |= 1 << Flags.ZERO
        elif result < 0.0:
            flags |= 1 << Flags.NEGATIVE
        elif result > 0.0:
            flags |= 1 << Flags.POSITIVE

        # Overflow si el resultado es infinito
        if result == float("inf") or result == float("-inf"):
            flags |= 1 << Flags.OVERFLOW

        return flags
