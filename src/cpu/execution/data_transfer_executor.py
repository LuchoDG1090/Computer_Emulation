"""
Ejecutor de instrucciones de transferencia de datos
"""

from typing import Any, Dict

from src.cpu.core import ALU, ALUOperation
from src.cpu.io_ports import IOPorts
from src.cpu.memory_ops import MemoryOperations
from src.cpu.registers import RegisterFile
from src.isa.isa import Opcodes


class DataTransferExecutor:
    """Ejecuta instrucciones de transferencia de datos (MOVI, LD, ST, IN, OUT, etc.)"""

    def __init__(
        self,
        registers: RegisterFile,
        memory_ops: MemoryOperations,
        io_ports: IOPorts,
    ):
        """
        Inicializa el ejecutor de transferencia de datos

        Args:
            registers: Banco de registros
            memory_ops: Operaciones de memoria
            io_ports: Operaciones de I/O
        """
        self.registers = registers
        self.memory_ops = memory_ops
        self.io_ports = io_ports
        self.alu = ALU()  # Para ADDI

    def execute(self, instruction: Dict[str, Any], cpu) -> bool:
        """
        Ejecuta una instrucción de transferencia de datos

        Args:
            instruction: Instrucción decodificada
            cpu: Referencia a la CPU

        Returns:
            True para continuar ejecución
        """
        opcode = instruction["opcode"]

        handlers = {
            Opcodes.MOVI: self._execute_movi,
            Opcodes.LD: self._execute_ld,
            Opcodes.ST: self._execute_st,
            Opcodes.OUT: self._execute_out,
            Opcodes.IN: self._execute_in,
            Opcodes.ADDI: self._execute_addi,
            Opcodes.CP: self._execute_cp,
            Opcodes.INS: self._execute_ins,
            Opcodes.OUTS: self._execute_outs,
        }

        handler = handlers.get(opcode)
        if handler:
            handler(instruction, cpu)

        return True

    def _execute_movi(self, instruction: Dict[str, Any], cpu):
        """MOVI Rd, Rs1 o MOVI Rd, #imm"""
        rd = instruction["rd"]
        rs1 = instruction["rs1"]
        imm32 = instruction["imm32"]
        func = instruction["func"]

        if func == 0:  # Inmediato
            self.registers[rd] = imm32
        else:  # Registro a registro
            self.registers[rd] = self.registers[rs1]

    def _execute_ld(self, instruction: Dict[str, Any], cpu):
        """LD Rd, Rs1 + offset o LD Rd, #address"""
        rd = instruction["rd"]
        rs1 = instruction["rs1"]
        imm32 = instruction["imm32"]
        func = instruction["func"]

        if func == 0:  # Dirección absoluta
            address = imm32
        else:  # Offset desde registro base
            address = self.registers[rs1] + self.memory_ops.sign_extend_32(imm32)

        value = self.memory_ops.read_word(address)
        self.registers[rd] = value

    def _execute_st(self, instruction: Dict[str, Any], cpu):
        """ST Rd, #address o ST Rd, [Rs1 + offset]"""
        rd = instruction["rd"]
        rs1 = instruction["rs1"]
        imm32 = instruction["imm32"]
        func = instruction["func"]

        if func == 0:  # Dirección absoluta: ST Rd, #address
            address = imm32
            value = self.registers[rd]
        else:  # Offset desde registro base: ST Rd, [Rs1 + offset]
            address = self.registers[rs1] + self.memory_ops.sign_extend_32(imm32)
            value = self.registers[rd]

        self.memory_ops.write_word(address, value)

    def _execute_out(self, instruction: Dict[str, Any], cpu):
        """OUT Rs1/Rd, port/mmio"""
        rd = instruction["rd"]
        rs1 = instruction["rs1"]
        imm32 = instruction["imm32"]
        func = instruction["func"]

        # Aceptar ambas codificaciones (compatibilidad)
        src_reg_val = self.registers[rs1] if rs1 != 0 else self.registers[rd]

        self.io_ports.write_output(src_reg_val, imm32, func)

    def _execute_in(self, instruction: Dict[str, Any], cpu):
        """IN Rd, port/mmio"""
        rd = instruction["rd"]
        rs1 = instruction["rs1"]
        imm32 = instruction["imm32"]
        func = instruction["func"]

        # Suboperación extendida: parse línea de enteros
        subop = (func >> 1) & 0x7
        sep_chr = (func >> 4) & 0xFF

        if subop == 1:
            # Parse array de enteros en memoria
            base = self.registers[rs1]
            count = imm32 & 0xFFFFFFFF

            # Leer línea (debe venir de callback)
            line = ""
            if self.io_ports.input_char_callback:
                # Simular lectura de línea completa
                chars = []
                while True:
                    ch = self.io_ports.input_char_callback()
                    if ch == 10 or ch == 0:  # \n o null
                        break
                    chars.append(chr(ch))
                line = "".join(chars)

            # Separar y parsear
            parts = line.split(chr(sep_chr)) if sep_chr else line.split()
            parsed_count = 0

            for i in range(min(count, len(parts))):
                try:
                    val = int(parts[i], 0)
                except ValueError:
                    val = 0

                addr = base + i * 8
                if self.memory_ops.is_valid_address(addr):
                    self.memory_ops.write_word(addr, val)
                    parsed_count += 1

            self.registers[rd] = parsed_count
        else:
            # IN normal
            value = self.io_ports.read_input(imm32, func)
            self.registers[rd] = value

    def _execute_addi(self, instruction: Dict[str, Any], cpu):
        """ADDI Rd, Rs1, #imm32"""
        rd = instruction["rd"]
        rs1 = instruction["rs1"]
        imm32 = instruction["imm32"]

        operand1 = self.registers[rs1]
        operand2 = self.memory_ops.sign_extend_32(imm32)

        result, flags = self.alu.execute(ALUOperation.ADD, operand1, operand2)

        self.registers[rd] = result & 0xFFFFFFFFFFFFFFFF
        cpu.flags = flags

    def _execute_cp(self, instruction: Dict[str, Any], cpu):
        """CP Rd, Rs1 (copia registro sin afectar flags)"""
        rd = instruction["rd"]
        rs1 = instruction["rs1"]

        self.registers[rd] = self.registers[rs1]

    def _execute_ins(self, instruction: Dict[str, Any], cpu):
        """
        INS Rd, PORT - Lee string desde puerto

        Puertos:
        - 0xFFFF0018: Consola
        - 0xFFFF0020+: Archivos (deben estar abiertos)
        """
        rd = instruction["rd"]
        port = instruction["imm32"]

        buffer_addr = self.registers[rd]

        # Leer string desde puerto
        text = self.io_ports.read_string(port, max_length=1000)

        # Guardar en memoria
        self.io_ports.write_string_to_memory(buffer_addr, text, max_length=1000)

    def _execute_outs(self, instruction: Dict[str, Any], cpu):
        """
        OUTS Rd, PORT - Escribe string a puerto

        Puertos:
        - 0xFFFF0008: Consola
        - 0xFFFF0020+: Archivos (deben estar abiertos)
        """
        rd = instruction["rd"]
        port = instruction["imm32"]

        string_addr = self.registers[rd]

        # Leer string desde memoria
        text = self.io_ports.read_string_from_memory(string_addr, max_length=1000)

        # Escribir a puerto
        self.io_ports.write_string(text, port)
