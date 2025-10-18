"""Ensamblador principal"""

from src.assembler.encoder import InstructionEncoder
from src.assembler.exceptions import EncodingError
from src.assembler.lexer import lexer
from src.assembler.memory_map import MemoryMap
from src.assembler.parser import Directive, Instruction, InstructionParser
from src.assembler.symbol_table import SymbolTable


class Assembler:
    """Ensamblador de dos pasadas con PLY"""

    def __init__(self):
        self.encoder = InstructionEncoder()
        self.symbol_table = SymbolTable()
        self.memory_map = MemoryMap()
        self.parser = InstructionParser()
        self.word_size = 8  # 64 bits

    def assemble_file(self, input_file, output_binary, output_map=None):
        """Ensambla un archivo"""
        source_code = self._read_file(input_file)
        binary_output = self.assemble(source_code)

        self._write_binary(output_binary, binary_output)
        self._write_map(output_map)
        self._print_summary(output_binary, output_map)

    def assemble(self, source_code):
        """Ensambla código fuente"""
        self._reset_state()
        parsed_lines = self._first_pass(source_code)
        binary_output = self._second_pass(parsed_lines)
        return binary_output

    # === Primera Pasada ===

    def _first_pass(self, source_code):
        """Primera pasada: identificar etiquetas y parsear"""
        lexer.input(source_code)
        parsed_lines = []
        current_address = 0

        for line_tokens in self._group_tokens_by_line(lexer):
            label, item, current_address = self._process_line(
                line_tokens, current_address
            )

            if label:
                self.symbol_table.add(label, current_address)

            if item:
                item.address = current_address
                parsed_lines.append(item)
                current_address = self._advance_address(item, current_address)

        return parsed_lines

    def _group_tokens_by_line(self, lexer):
        """Agrupa tokens por línea"""
        current_line = []

        for token in lexer:
            if token.type == "NEWLINE":
                if current_line:
                    yield current_line
                    current_line = []
            else:
                current_line.append(token)

        # Última línea sin newline
        if current_line:
            yield current_line

    def _process_line(self, tokens, current_address):
        """Procesa una línea de tokens"""
        if not tokens:
            return None, None, current_address

        label, item = self.parser.parse_line(tokens)
        return label, item, current_address

    def _advance_address(self, item, current_address):
        """Calcula la siguiente dirección según el tipo de item"""
        if isinstance(item, Instruction):
            return current_address + self.word_size

        if isinstance(item, Directive):
            return self._calculate_directive_address(item, current_address)

        return current_address

    # === Segunda Pasada ===

    def _second_pass(self, parsed_lines):
        """Segunda pasada: generar código binario"""
        binary_lines = []

        for item in parsed_lines:
            codes = self._generate_binary(item)
            if codes:
                binary_lines.extend(codes if isinstance(codes, list) else [codes])

        return "\n".join(binary_lines)

    def _generate_binary(self, item):
        """Genera código binario para un item"""
        if isinstance(item, Instruction):
            return self._generate_instruction_binary(item)

        if isinstance(item, Directive):
            return self._generate_directive_binary(item)

        return None

    def _generate_instruction_binary(self, instruction):
        """Genera binario para una instrucción"""
        try:
            binary_code = self._encode_instruction(instruction)
            self.memory_map.mark_executable(instruction.address)
            return binary_code
        except Exception as e:
            raise EncodingError(
                f"Error en {instruction.mnemonic} @ {instruction.address:#x}: {e}"
            )

    def _generate_directive_binary(self, directive):
        """Genera binario para una directiva"""
        handlers = {
            "ORG": self._handle_org,
            "DW": self._handle_dw,
            "RESW": self._handle_resw,
        }

        handler = handlers.get(directive.name)
        if handler:
            return handler(directive)

        return []

    # === Codificación ===

    def _encode_instruction(self, instruction):
        """Codifica una instrucción a binario"""
        resolved_operands = self._resolve_operands(instruction.operands)
        instruction_word = self.encoder.encode_instruction(
            instruction.mnemonic, resolved_operands
        )
        return self.encoder.to_binary_string(instruction_word)

    def _resolve_operands(self, operands):
        """Resuelve etiquetas a direcciones"""
        resolved = []
        for op in operands:
            # Detectar [etiqueta]
            if isinstance(op, str) and op.startswith("[") and op.endswith("]"):
                label = op[1:-1]  # Quitar corchetes
                if self.symbol_table.exists(label):
                    resolved.append(self.symbol_table.get(label))
                else:
                    resolved.append(op)  # Mantener como está si no existe
            elif isinstance(op, str) and self.symbol_table.exists(op):
                resolved.append(self.symbol_table.get(op))
            else:
                resolved.append(op)
        return resolved

    # === Directivas ===

    def _handle_org(self, directive):
        """Procesa directiva ORG"""
        return []

    def _handle_dw(self, directive):
        """Procesa directiva DW (Define Word)"""
        binary_lines = []
        for value in directive.args:
            resolved_value = self._resolve_value(value)
            binary_lines.append(format(resolved_value & 0xFFFFFFFFFFFFFFFF, "064b"))
            self.memory_map.mark_data(directive.address)
        return binary_lines

    def _handle_resw(self, directive):
        """Procesa directiva RESW (Reserve Words)"""
        count = directive.args[0] if directive.args else 1
        binary_lines = ["0" * 64 for _ in range(count)]

        for _ in range(count):
            self.memory_map.mark_data(directive.address)

        return binary_lines

    def _resolve_value(self, value):
        """Resuelve un valor (puede ser etiqueta)"""
        if isinstance(value, str) and self.symbol_table.exists(value):
            return self.symbol_table.get(value)
        return value

    def _calculate_directive_address(self, directive, current_address):
        """Calcula dirección después de una directiva"""
        if directive.name == "ORG":
            return directive.args[0] if directive.args else current_address

        if directive.name == "DW":
            return current_address + (len(directive.args) * self.word_size)

        if directive.name == "RESW":
            count = directive.args[0] if directive.args else 1
            return current_address + (count * self.word_size)

        return current_address

    # === Utilidades ===

    def _reset_state(self):
        """Reinicia el estado del ensamblador"""
        self.symbol_table.clear()
        self.memory_map = MemoryMap()
        self.parser.current_address = 0

    def _read_file(self, filepath):
        """Lee un archivo"""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _write_binary(self, filepath, content):
        """Escribe archivo binario"""
        with open(filepath, "w") as f:
            f.write(content)

    def _write_map(self, filepath):
        """Escribe archivo de mapa de memoria"""
        if not filepath:
            return

        if filepath.endswith(".exec"):
            self.memory_map.save_exec_format(filepath)
        else:
            self.memory_map.save_map_format(filepath)

    def _print_summary(self, output_binary, output_map):
        """Imprime resumen del ensamblado"""
        print("✓ Ensamblado completado")
        print(f"  Binario: {output_binary}")
        if output_map:
            print(f"  Mapa: {output_map}")
