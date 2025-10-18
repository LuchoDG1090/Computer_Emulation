from cpu.isa import InstructionType, Opcodes, opcode_to_type


class Encoder:
    def __init__(self):
        """Inicializa el codificador con mapeo de tipos de instruccion"""
        pass

    def r_type(self, opcode: int, rd: int, rs1: int, rs2: int, func: int = 0) -> int:
        """
        Codifica una instruccion R-Type (registro-registro)

        Args:
            opcode: Codigo de operacion (8 bits)
            rd: Registro destino (4 bits, 0-15)
            rs1: Registro fuente 1 (4 bits, 0-15)
            rs2: Registro fuente 2 (4 bits, 0-15)
            func: Campo de funcion/modificador (12 bits)

        Returns:
            Instruccion codificada de 64 bits
        """
        instruction = 0
        instruction |= (opcode & 0xFF) << 56
        instruction |= (rd & 0xF) << 52
        instruction |= (rs1 & 0xF) << 48
        instruction |= (rs2 & 0xF) << 44
        instruction |= (func & 0xFFF) << 32
        # IMM32 = 0 para R-Type

        return instruction

    def i_type(self, opcode: int, rd: int, rs1: int, imm32: int, func: int = 0) -> int:
        """
        Codifica una instruccion I-Type (inmediato/direccion)

        Args:
            opcode: Codigo de operacion (8 bits)
            rd: Registro destino (4 bits, 0-15)
            rs1: Registro fuente 1 (4 bits, 0-15)
            imm32: Inmediato o direccion (32 bits)
            func: Campo de funcion/modificador (12 bits)

        Returns:
            Instruccion codificada de 64 bits
        """
        instruction = 0
        instruction |= (opcode & 0xFF) << 56
        instruction |= (rd & 0xF) << 52
        instruction |= (rs1 & 0xF) << 48
        # RS2 = 0 para I-Type (o puede usarse como parte de func)
        instruction |= (func & 0xFFF) << 32
        instruction |= imm32 & 0xFFFFFFFF

        return instruction

    def j_type(self, opcode: int, address: int, func: int = 0) -> int:
        """
        Codifica una instruccion J-Type (salto/llamada)

        Args:
            opcode: Codigo de operacion (8 bits)
            address: Direccion de salto (32 bits)
            func: Campo de funcion/modificador (12 bits)

        Returns:
            Instruccion codificada de 64 bits
        """
        instruction = 0
        instruction |= (opcode & 0xFF) << 56
        # RD, RS1, RS2 = 0 para J-Type basico
        instruction |= (func & 0xFFF) << 32
        instruction |= address & 0xFFFFFFFF

        return instruction

    def s_type(self, opcode: int, func: int = 0) -> int:
        """
        Codifica una instruccion S-Type (sistema)

        Args:
            opcode: Codigo de operacion (8 bits)
            func: Campo de funcion/modificador (12 bits)

        Returns:
            Instruccion codificada de 64 bits
        """
        instruction = 0
        instruction |= (opcode & 0xFF) << 56
        # Todos los demas campos = 0 para S-Type basico
        instruction |= (func & 0xFFF) << 32

        return instruction

    def encode(
        self,
        opcode: int,
        rd: int = 0,
        rs1: int = 0,
        rs2: int = 0,
        func: int = 0,
        imm32: int = 0,
    ) -> int:
        """
        Metodo de codificacion generico (mantiene compatibilidad)
        Determina automaticamente el tipo basado en el opcode

        Args:
            opcode: Codigo de operacion
            rd: Registro destino
            rs1: Registro fuente 1
            rs2: Registro fuente 2
            func: Campo de funcion
            imm32: Inmediato/direccion

        Returns:
            Instruccion codificada
        """
        inst_type = opcode_to_type.get(opcode, InstructionType.S_TYPE)

        if inst_type == InstructionType.R_TYPE:
            return self.r_type(opcode, rd, rs1, rs2, func)
        elif inst_type == InstructionType.I_TYPE:
            return self.i_type(opcode, rd, rs1, imm32, func)
        elif inst_type == InstructionType.J_TYPE:
            return self.j_type(opcode, imm32, func)
        else:  # S_TYPE
            return self.s_type(opcode, func)

    def mnemonic_to_opcode(self, mnemonic: str) -> int:
        try:
            return Opcodes[mnemonic.upper()].value
        except KeyError:
            raise ValueError(f"Instrucción desconocida: {mnemonic}")

    def reg_to_num(self, reg: str) -> int:
        reg = reg.strip().upper().rstrip(",")
        if not reg.startswith("R"):
            raise ValueError(f"Registro inválido: {reg}")
        return int(reg[1:])
