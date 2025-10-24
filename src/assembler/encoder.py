"""Encoder de instrucciones a formato binario de 64 bits"""

import struct

from src.isa.isa import InstructionType, Opcodes, opcode_to_type


class InstructionEncoder:
    """Codifica instrucciones a formato binario de 64 bits"""

    def __init__(self):
        self.word_size = 8  # 64 bits = 8 bytes

    def encode_instruction(self, mnemonic, operands):
        """
        Codifica una instrucción completa desde mnemónico y operandos

        Args:
            mnemonic (str): Nombre de la instrucción ('ADD', 'MOVI', etc.)
            operands (list): Lista de operandos (registros, inmediatos, etc.)

        Returns:
            int: Instrucción codificada en 64 bits

        Formato de 64 bits:
            [63-56]: Opcode (8 bits)
            [55-52]: RD (4 bits)
            [51-48]: RS1 (4 bits)
            [47-44]: RS2 (4 bits)
            [43-32]: FUNC (12 bits)
            [31-0]:  IMM32 (32 bits)
        """
        # Obtener opcode
        try:
            opcode_enum = Opcodes[mnemonic]
            opcode = opcode_enum.value
        except KeyError:
            raise ValueError(f"Instrucción desconocida: {mnemonic}")

        # Determinar tipo de instrucción
        inst_type = opcode_to_type.get(opcode_enum, InstructionType.S_TYPE)

        # Codificar según el tipo
        if inst_type == InstructionType.R_TYPE:
            return self._encode_r_type(opcode, operands)
        elif inst_type == InstructionType.I_TYPE:
            return self._encode_i_type(opcode, operands)
        elif inst_type == InstructionType.J_TYPE:
            return self._encode_j_type(opcode, operands)
        elif inst_type == InstructionType.S_TYPE:
            return self._encode_s_type(opcode)
        else:
            raise ValueError(f"Tipo de instrucción desconocido para {mnemonic}")

    def _encode_r_type(self, opcode, operands):
        """
        R-Type: Operaciones registro-registro
        Formato: ADD RD, RS1, RS2
        Usa: RD, RS1, RS2
        """
        # Soportar forma abreviada de CMP con 2 operandos: CMP RS1, RS2
        if len(operands) == 2 and opcode == Opcodes.CMP.value:
            rd = 0  # RD no se usa para CMP (solo actualiza flags)
            rs1 = self._parse_register(operands[0])
            rs2 = self._parse_register(operands[1])
            return self._build_instruction(opcode, rd, rs1, rs2, 0, 0)

        if len(operands) < 3:
            raise ValueError(f"R-Type requiere 3 operandos, recibió {len(operands)}")

        rd = self._parse_register(operands[0])
        rs1 = self._parse_register(operands[1])
        rs2 = self._parse_register(operands[2])

        return self._build_instruction(opcode, rd, rs1, rs2, 0, 0)

    def _encode_i_type(self, opcode, operands):
        """
        I-Type: Operaciones con inmediato
        Formatos:
            - MOVI RD, IMM32
            - ADDI RD, RS1, IMM32
            - LD RD, IMM32
            - ST RD, IMM32
            - CP RD, RS1 (copia registro a registro)
            - PUSH RS1 | PUSH #imm (1 operando)
            - POP RD (1 operando)
        """
        # Instrucciones de 1 operando: PUSH/POP
        if opcode == Opcodes.PUSH.value:
            if len(operands) != 1:
                raise ValueError(f"PUSH requiere 1 operando, recibió {len(operands)}")
            op = operands[0]
            # PUSH de registro
            if isinstance(op, int) or (isinstance(op, str) and op.startswith("R")):
                rs1 = self._parse_register(op)
                return self._build_instruction(opcode, 0, rs1, 0, 1, 0)
            # PUSH inmediato
            imm32 = self._parse_immediate(op)
            return self._build_instruction(opcode, 0, 0, 0, 0, imm32)

        if opcode == Opcodes.POP.value:
            if len(operands) != 1:
                raise ValueError(f"POP requiere 1 operando, recibió {len(operands)}")
            rd = self._parse_register(operands[0])
            return self._build_instruction(opcode, rd, 0, 0, 0, 0)

        rd = self._parse_register(operands[0])

        # Caso especial: CP usa dos registros, no inmediato
        if opcode == Opcodes.CP.value and len(operands) == 2:
            rs1 = self._parse_register(operands[1])
            imm32 = 1  # Indicador para el decoder
            return self._build_instruction(opcode, rd, rs1, 0, 1, imm32)

        if len(operands) == 2:
            # Formato: MOVI RD, IMM32 o LD RD, IMM32 o OUT RD, PORT
            rs1 = 0
            imm32_raw = operands[1]
            imm32 = self._parse_immediate(imm32_raw)

            # Si es MOVI con flotante, marcar con FUNC=2 para que el CPU lo sepa
            if opcode == Opcodes.MOVI.value and isinstance(imm32_raw, float):
                func = 2  # Indica que es un float (single precision en IMM32)
            else:
                func = 0
        elif len(operands) == 3:
            # Formato: ADDI RD, RS1, IMM32 o IN/OUT variantes
            op2_val = operands[1]
            op3_val = operands[2]

            if opcode == Opcodes.IN.value:
                # Dos variantes soportadas:
                # 1) IN RD, PORT, FUNC  -> lectura simple (puerto/MMIO)
                # 2) IN RD, RS1, COUNT  -> lectura extendida de línea de enteros a memoria
                #    RS1 = base del array, IMM32 = cantidad máx.
                if (
                    isinstance(op2_val, (int, str))
                    and (
                        isinstance(op2_val, int)
                        or (isinstance(op2_val, str) and op2_val.startswith("R"))
                    )
                    and not (isinstance(op3_val, str) and op3_val.startswith("R"))
                ):
                    # Si segundo operando es registro y tercero es inmediato: modo extendido a memoria
                    rs1 = self._parse_register(op2_val)
                    imm32 = self._parse_immediate(op3_val)  # COUNT
                    # FUNC por defecto: subop=1 (parse array) y separador=' ' (0x20)
                    # Bits: [3:1]=1, [11:4]=0x20
                    func = ((0x20 & 0xFF) << 4) | (1 << 1)
                else:
                    # IN RD, PORT, FUNC - el tercer operando es FUNC explícito
                    imm32 = self._parse_immediate(op2_val)  # PORT
                    func = self._parse_immediate(op3_val)  # FUNC
                    rs1 = 0
            elif opcode == Opcodes.OUT.value:
                # OUT RD, PORT, FUNC - el tercer operando es FUNC explícito
                imm32 = self._parse_immediate(op2_val)  # PORT
                func = self._parse_immediate(op3_val)  # FUNC
                rs1 = 0
            elif opcode == Opcodes.LD.value or opcode == Opcodes.ST.value:
                # LD/ST RD, RS1, OFFSET - modo de direccionamiento relativo
                rs1 = self._parse_register(op2_val)
                imm32 = self._parse_immediate(op3_val)  # offset
                func = 1  # indica modo relativo (rs1 + offset)
            else:
                # Instrucción normal de 3 operandos (ADDI, etc)
                rs1 = self._parse_register(op2_val)
                imm32 = self._parse_immediate(op3_val)
                func = 0

            return self._build_instruction(opcode, rd, rs1, 0, func, imm32)
        else:
            raise ValueError(
                f"I-Type requiere 2 o 3 operandos, recibió {len(operands)}"
            )

        return self._build_instruction(opcode, rd, rs1, 0, func, imm32)

    def _encode_j_type(self, opcode, operands):
        """
        J-Type: Instrucciones de salto
        Formatos:
            - JMP ADDRESS
            - CALL ADDRESS
            - RET (sin operandos)
        """
        if len(operands) == 0:
            # RET no necesita operandos
            imm32 = 0
        else:
            # JMP, CALL, etc.
            imm32 = self._parse_immediate(operands[0])

        return self._build_instruction(opcode, 0, 0, 0, 0, imm32)

    def _encode_s_type(self, opcode):
        """
        S-Type: Instrucciones sin operandos
        Formato: HALT, NOP
        """
        return self._build_instruction(opcode, 0, 0, 0, 0, 0)

    def _build_instruction(self, opcode, rd, rs1, rs2, func, imm32):
        """
        Construye la instrucción de 64 bits

        Args:
            opcode (int): Código de operación (8 bits)
            rd (int): Registro destino (4 bits)
            rs1 (int): Registro fuente 1 (4 bits)
            rs2 (int): Registro fuente 2 (4 bits)
            func (int): Campo de función (12 bits)
            imm32 (int): Inmediato/dirección (32 bits)

        Returns:
            int: Instrucción de 64 bits
        """
        instruction = 0
        instruction |= (opcode & 0xFF) << 56  # [63-56] Opcode
        instruction |= (rd & 0xF) << 52  # [55-52] RD
        instruction |= (rs1 & 0xF) << 48  # [51-48] RS1
        instruction |= (rs2 & 0xF) << 44  # [47-44] RS2
        instruction |= (func & 0xFFF) << 32  # [43-32] FUNC
        instruction |= imm32 & 0xFFFFFFFF  # [31-0]  IMM32
        return instruction

    def _parse_register(self, operand):
        """
        Parsea un operando de registro

        Args:
            operand: Puede ser int (0-15) o string 'R0'-'R15'

        Returns:
            int: Número de registro (0-15)
        """
        if isinstance(operand, int):
            if 0 <= operand <= 15:
                return operand
            raise ValueError(f"Registro fuera de rango: {operand} (debe ser 0-15)")

        # Si es string, intentar parsearlo
        if isinstance(operand, str) and operand.startswith("R"):
            try:
                reg_num = int(operand[1:])
                if 0 <= reg_num <= 15:
                    return reg_num
            except ValueError:
                pass

        raise ValueError(f"Operando inválido como registro: {operand}")

    def _parse_immediate(self, operand):
        """
        Parsea un operando inmediato

        Args:
            operand: Valor inmediato (int, float o dirección)

        Returns:
            int: Valor inmediato de 32 bits (o representación especial para floats)
        """
        if isinstance(operand, float):
            # Para flotantes, convertir a representación IEEE 754
            # Usamos single precision (32 bits) para que quepa en IMM32
            float_bits = struct.unpack("I", struct.pack("f", operand))[0]
            return float_bits

        if isinstance(operand, int):
            # Asegurar que cabe en 32 bits (signed)
            if -2147483648 <= operand <= 4294967295:
                return operand & 0xFFFFFFFF
            raise ValueError(f"Inmediato fuera de rango: {operand}")

        raise ValueError(f"Operando inválido como inmediato: {operand}")

    def to_binary_string(self, instruction):
        """
        Convierte instrucción a cadena binaria de 64 bits

        Args:
            instruction (int): Instrucción codificada

        Returns:
            str: Representación binaria (64 caracteres)
        """
        return format(instruction & 0xFFFFFFFFFFFFFFFF, "064b")

    def to_hex_string(self, instruction):
        """
        Convierte instrucción a cadena hexadecimal

        Args:
            instruction (int): Instrucción codificada

        Returns:
            str: Representación hexadecimal (16 caracteres)
        """
        return format(instruction & 0xFFFFFFFFFFFFFFFF, "016X")
