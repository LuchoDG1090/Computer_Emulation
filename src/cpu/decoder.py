from typing import Any, Dict

from src.isa.isa import InstructionType, opcode_to_type


class Decoder:
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
            "opcode": opcode,
            "type": inst_type,
            "rd": rd,
            "rs1": rs1,
            "rs2": rs2,
            "func": func,
            "imm32": imm32,
        }
