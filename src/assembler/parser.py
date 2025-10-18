"""Parser de instrucciones"""

from src.assembler.exceptions import ParserError


class Instruction:
    """Representa una instrucción parseada"""

    def __init__(self, address, mnemonic, operands=None):
        self.address = address
        self.mnemonic = mnemonic
        self.operands = operands or []

    def __repr__(self):
        return f"Instruction({self.address:#x}, {self.mnemonic}, {self.operands})"


class Directive:
    """Representa una directiva parseada"""

    def __init__(self, address, name, args=None):
        self.address = address
        self.name = name
        self.args = args or []

    def __repr__(self):
        return f"Directive({self.address:#x}, {self.name}, {self.args})"


class InstructionParser:
    """Parsea tokens en instrucciones y directivas"""

    def __init__(self):
        self.current_address = 0
        self.word_size = 8  # 64 bits = 8 bytes

    def parse_line(self, tokens):
        """Parsea una línea de tokens"""
        if not tokens:
            return None, None

        label, remaining_tokens = self._extract_label(tokens)

        if not remaining_tokens:
            return label, None

        instruction = self._parse_item(remaining_tokens)
        return label, instruction

    def _extract_label(self, tokens):
        """Extrae etiqueta si existe"""
        if tokens[0].type == "LABEL":
            return tokens[0].value, tokens[1:]
        return None, tokens

    def _parse_item(self, tokens):
        """Parsea instrucción o directiva"""
        first_token = tokens[0]

        if first_token.type == "DIRECTIVE":
            return self._parse_directive(first_token, tokens[1:])

        if first_token.type == "OPCODE":
            return self._parse_instruction(first_token, tokens[1:])

        raise ParserError(f"Token inesperado: {first_token.type}")

    # === Parseo de Instrucciones ===

    def _parse_instruction(self, opcode_token, operand_tokens):
        """Parsea una instrucción"""
        mnemonic = opcode_token.value
        operands = self._extract_operands(operand_tokens)
        return Instruction(self.current_address, mnemonic, operands)

    def _extract_operands(self, tokens):
        """Extrae operandos de tokens"""
        operands = []
        i = 0

        while i < len(tokens):
            operand, consumed = self._parse_next_operand(tokens, i)

            if operand is not None:
                operands.append(operand)

            i += consumed

        return operands

    def _parse_next_operand(self, tokens, index):
        """
        Parsea el siguiente operando

        Returns:
            tuple: (operando, tokens_consumidos)
        """
        if index >= len(tokens):
            return None, 0

        token = tokens[index]

        # Ignorar delimitadores
        if token.type in ("COMMA", "NEWLINE"):
            return None, 1

        # Detectar [identificador]
        if token.type == "LBRACKET":
            return self._parse_bracketed_operand(tokens, index)

        # Operandos simples
        if token.type in ("REGISTER", "IMMEDIATE", "OPCODE", "IDENTIFIER"):
            return token.value, 1

        return None, 1

    def _parse_bracketed_operand(self, tokens, index):
        """
        Parsea operando con corchetes [identifier]

        Returns:
            tuple: (operando, tokens_consumidos)
        """
        # Verificar que hay suficientes tokens: [, identifier, ]
        if index + 2 >= len(tokens):
            return None, 1

        # Verificar estructura completa
        has_identifier = tokens[index + 1].type in ("IDENTIFIER", "OPCODE")
        has_closing = tokens[index + 2].type == "RBRACKET"

        if not (has_identifier and has_closing):
            return None, 1

        identifier = tokens[index + 1].value
        return f"[{identifier}]", 3  # Consume [, identifier, ]

    # === Parseo de Directivas ===

    def _parse_directive(self, directive_token, arg_tokens):
        """Parsea una directiva"""
        name = directive_token.value
        args = self._extract_directive_args(arg_tokens)
        return Directive(self.current_address, name, args)

    def _extract_directive_args(self, tokens):
        """Extrae argumentos de directiva"""
        args = []

        for token in tokens:
            if self._is_valid_arg_token(token):
                args.append(token.value)

        return args

    def _is_valid_arg_token(self, token):
        """Verifica si es un token válido para argumento de directiva"""
        return token.type in ("IMMEDIATE", "REGISTER", "OPCODE", "IDENTIFIER")
