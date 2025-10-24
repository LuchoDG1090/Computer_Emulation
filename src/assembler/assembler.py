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
        self.address_word_index = {}

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
        word_index = 0

        for line_no, line_tokens in self._group_tokens_by_line(lexer):
            label, item, current_address = self._process_line(
                line_tokens, current_address
            )

            if label:
                self.symbol_table.add(label, current_address)

            if item:
                item.address = current_address
                item.line_no = line_no
                self._register_word_indices(item, word_index)
                parsed_lines.append(item)
                word_index += self._words_generated(item)
                current_address = self._advance_address(item, current_address)

        return parsed_lines

    def _group_tokens_by_line(self, lexer):
        """Agrupa tokens por línea"""
        current_line = []
        current_line_no = None

        for token in lexer:
            if token.type == "NEWLINE":
                if current_line:
                    yield current_line_no, current_line
                    current_line = []
                    current_line_no = None
            else:
                if current_line_no is None:
                    current_line_no = token.lineno
                current_line.append(token)

        # Última línea sin newline
        if current_line:
            yield current_line_no, current_line

    def _process_line(self, tokens, current_address):
        """Procesa una línea de tokens"""
        if not tokens:
            return None, None, current_address

        label, item = self.parser.parse_line(tokens)
        return label, item, current_address

    def _advance_address(self, item, current_address):
        """Calcula la siguiente dirección según el tipo de item"""
        if isinstance(item, Instruction):
            # Avanza una palabra en bytes (64 bits = 8 bytes)
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
            index = self.address_word_index.get(instruction.address)
            self.memory_map.mark_executable(instruction.address, index)
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
            "DB": self._handle_db,
        }

        handler = handlers.get(directive.name)
        if handler:
            return handler(directive)

        return []

    # === Codificación ===

    def _encode_instruction(self, instruction):
        """Codifica una instrucción a binario"""
        resolved_operands, relocations = self._resolve_operands(instruction)
        instruction_word = self.encoder.encode_instruction(
            instruction.mnemonic, resolved_operands
        )
        binary_code = self.encoder.to_binary_string(instruction_word)
        if not relocations:
            return binary_code

        # For relocatable operands, replace the immediate field with the placeholder
        # Para operandos reubicables, reemplazar el campo inmediato con el marcador
        prefix = binary_code[:32]
        # Currently only one relocation per instruction is expected
        # Actualmente solo se espera una reubicación por instrucción
        placeholder = relocations[0]["placeholder"]
        return f"{prefix}{placeholder}"

    def _resolve_operands(self, instruction):
        """Resuelve operandos y detecta referencias reubicables"""
        resolved = []
        relocations = []

        for index, op in enumerate(instruction.operands):
            label = None

            if isinstance(op, str) and op.startswith("[") and op.endswith("]"):
                label = op[1:-1]
            elif isinstance(op, str) and self.symbol_table.exists(op):
                label = op

            if label and self.symbol_table.exists(label):
                placeholder = self._get_placeholder_for_label(label)
                resolved.append(0)
                relocations.append({"operand_index": index, "placeholder": placeholder})
            else:
                resolved.append(op)

        return resolved, relocations

    # === Directivas ===

    def _handle_org(self, directive):
        """Procesa directiva ORG"""
        return []

    def _handle_dw(self, directive):
        """Procesa directiva DW (Define Word)"""
        binary_lines = []
        for offset, value in enumerate(directive.args):
            resolved_value = self._resolve_value(value)
            if isinstance(resolved_value, str):
                binary_lines.append(resolved_value)
            else:
                binary_lines.append(format(resolved_value & 0xFFFFFFFFFFFFFFFF, "064b"))
            # Dirección expresada en bytes
            address = directive.address + (offset * self.word_size)
            index = self.address_word_index.get(address)
            self.memory_map.mark_data(address, index)
        return binary_lines

    def _handle_resw(self, directive):
        """Procesa directiva RESW (Reserve Words)"""
        count = directive.args[0] if directive.args else 1
        binary_lines = ["0" * 64 for _ in range(count)]

        for offset in range(count):
            # Dirección expresada en bytes
            address = directive.address + (offset * self.word_size)
            index = self.address_word_index.get(address)
            self.memory_map.mark_data(address, index)

        return binary_lines

    def _handle_db(self, directive):
        """Procesa directiva DB (Define Byte)"""
        bytes_data = []

        # Procesar cada argumento
        for arg in directive.args:
            if isinstance(arg, str):
                # Es una cadena de texto
                for char in arg:
                    bytes_data.append(ord(char))
            else:
                # Es un valor numérico (byte)
                bytes_data.append(arg & 0xFF)

        # Agrupar bytes en palabras de 8 bytes
        binary_lines = []
        word_count = (len(bytes_data) + 7) // 8  # Redondear hacia arriba

        for word_idx in range(word_count):
            word_value = 0
            start_byte = word_idx * 8
            end_byte = min(start_byte + 8, len(bytes_data))

            # Empaquetar bytes en una palabra (little-endian)
            for byte_idx in range(start_byte, end_byte):
                byte_offset = byte_idx - start_byte
                word_value |= bytes_data[byte_idx] << (byte_offset * 8)

            # Generar representación binaria
            binary_lines.append(format(word_value, "064b"))

            # Marcar en el mapa de memoria (dirección en bytes)
            address = directive.address + (word_idx * self.word_size)
            index = self.address_word_index.get(address)
            self.memory_map.mark_data(address, index)

        return binary_lines

    def _resolve_value(self, value):
        """Resuelve un valor (puede ser etiqueta)"""
        if isinstance(value, str) and self.symbol_table.exists(value):
            return self._get_placeholder_for_label(value)
        return value

    def _calculate_directive_address(self, directive, current_address):
        """Calcula dirección después de una directiva"""
        if directive.name == "ORG":
            # ORG define la posición de memoria en bytes
            return directive.args[0] if directive.args else current_address

        if directive.name == "DW":
            # Avanza tantas palabras (en bytes) como argumentos
            return current_address + (len(directive.args) * self.word_size)

        if directive.name == "RESW":
            count = directive.args[0] if directive.args else 1
            # Avanza 'count' palabras en bytes
            return current_address + (count * self.word_size)

        if directive.name == "DB":
            # Calcular cuántos bytes ocupan todos los argumentos
            total_bytes = 0
            for arg in directive.args:
                if isinstance(arg, str):
                    total_bytes += len(arg)
                else:
                    total_bytes += 1
            # Redondear hacia arriba al siguiente múltiplo de word_size
            word_count = (total_bytes + self.word_size - 1) // self.word_size
            # Avanza 'word_count' palabras en bytes
            return current_address + (word_count * self.word_size)

        return current_address

    # === Utilidades ===

    def _reset_state(self):
        """Reinicia el estado del ensamblador"""
        self.symbol_table.clear()
        self.memory_map = MemoryMap()
        self.parser.current_address = 0
        self.address_word_index = {}

    def _get_placeholder_for_label(self, label):
        """Obtiene el marcador de reubicación para una etiqueta"""
        address = self.symbol_table.get(label)
        index = self.address_word_index.get(address, 0)
        return f"{{{index}}}"

    def _words_generated(self, item):
        """Devuelve cuántas palabras de 64 bits produce un item"""
        if isinstance(item, Instruction):
            return 1

        if isinstance(item, Directive):
            if item.name == "ORG":
                return 0
            if item.name == "DW":
                return len(item.args)
            if item.name == "RESW":
                count = item.args[0] if item.args else 1
                return count
            if item.name == "DB":
                # Calcular cuántos bytes ocupan todos los argumentos
                total_bytes = 0
                for arg in item.args:
                    if isinstance(arg, str):
                        total_bytes += len(arg)
                    else:
                        total_bytes += 1
                # Redondear hacia arriba al siguiente múltiplo de word_size
                return (total_bytes + self.word_size - 1) // self.word_size

        return 0

    def _register_word_indices(self, item, base_index):
        """Registra el índice de palabra para cada dirección emitida"""
        if isinstance(item, Instruction):
            self.address_word_index[item.address] = base_index
            return

        if isinstance(item, Directive):
            if item.name == "ORG":
                return

            if item.name == "DW":
                for offset in range(len(item.args)):
                    # Dirección expresada en bytes
                    address = item.address + (offset * self.word_size)
                    self.address_word_index[address] = base_index + offset
                return

            if item.name == "RESW":
                count = item.args[0] if item.args else 1
                for offset in range(count):
                    # Dirección expresada en bytes
                    address = item.address + (offset * self.word_size)
                    self.address_word_index[address] = base_index + offset
                return

            if item.name == "DB":
                # Calcular número de palabras que ocupan los bytes
                total_bytes = 0
                for arg in item.args:
                    if isinstance(arg, str):
                        total_bytes += len(arg)
                    else:
                        total_bytes += 1
                word_count = (total_bytes + self.word_size - 1) // self.word_size

                for offset in range(word_count):
                    # Dirección expresada en bytes
                    address = item.address + (offset * self.word_size)
                    self.address_word_index[address] = base_index + offset

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

        self.memory_map.save_map_format(filepath)

    def _print_summary(self, output_binary, output_map):
        """Imprime resumen del ensamblado"""
        print("✓ Ensamblado completado")
        print(f"  Binario: {output_binary}")
        if output_map:
            print(f"  Mapa: {output_map}")
