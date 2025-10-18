"""
Módulo de puertos de entrada/salida (I/O) para la CPU
"""

from typing import Any, Callable, Dict, Optional

from src.memory.memory import Memory


class IOPorts:
    """Maneja operaciones de entrada/salida (IN/OUT) y MMIO"""

    # Direcciones MMIO
    MMIO_CONSOLE_CHAR = 0xFFFF0000  # Escribe byte (ASCII) a consola
    MMIO_CONSOLE_INT = 0xFFFF0008  # Imprime entero en consola
    MMIO_CONSOLE_IN_CHAR = 0xFFFF0010  # Lee un carácter (ASCII) desde consola
    MMIO_CONSOLE_IN_INT = 0xFFFF0018  # Lee un entero desde consola

    def __init__(self, memory: Memory, memory_size: int):
        """
        Inicializa puertos de I/O

        Args:
            memory: Objeto Memory
            memory_size: Tamaño de la memoria
        """
        self.mem = memory
        self.memory_size = memory_size

        # Callbacks para I/O (la GUI puede registrarlos)
        self.output_char_callback: Optional[Callable[[int], None]] = None
        self.output_int_callback: Optional[Callable[[int], None]] = None
        self.input_char_callback: Optional[Callable[[], int]] = None
        self.input_int_callback: Optional[Callable[[], int]] = None

        # Archivos abiertos para I/O de strings
        self.open_files: Dict[int, Any] = {}  # puerto -> file handle

        # Buffers de salida (para tests sin GUI)
        self.output_buffer: str = ""
        self.output_int_buffer: list = []

    # === Salida (OUT) ===

    def write_output(self, value: int, target: int, func: int):
        """
        Maneja instrucción OUT

        Args:
            value: Valor a escribir
            target: Puerto o dirección MMIO
            func: Campo FUNC (determina modo y suboperaciones)
        """
        mode_port = func & 1
        subop = (func >> 1) & 0x7
        sep_chr = (func >> 4) & 0xFF

        # Suboperación: imprimir array de enteros con separador
        if subop == 1:
            self._output_int_array(value, target, sep_chr)
            return

        # Suboperación: imprimir entero sin newline
        if subop == 2:
            self._output_int_no_newline(value)
            return

        # Operaciones normales
        if mode_port == 1:
            # Salida a puerto numérico
            self._output_to_port(value, target)
        else:
            # Salida a dirección MMIO
            self._output_to_mmio(value, target)

    def _output_to_port(self, value: int, port: int):
        """Escribe a puerto numérico"""
        if port == 1:
            self._write_char(value)
        elif port == 2:
            self._write_int(value)
        else:
            # Puerto desconocido
            if self.output_int_callback:
                self.output_int_callback(value)

    def _output_to_mmio(self, value: int, address: int):
        """Escribe a dirección MMIO"""
        if address == self.MMIO_CONSOLE_CHAR:
            self._write_char(value)
        elif address == self.MMIO_CONSOLE_INT:
            self._write_int(value)
        else:
            # MMIO genérico: escribir como memoria si está en rango
            if 0 <= address <= (self.memory_size - 8):
                self.mem.write_word(address, value & 0xFFFFFFFFFFFFFFFF)

    def _write_char(self, value: int):
        """Escribe un carácter (byte menos significativo)"""
        ch = value & 0xFF

        if self.output_char_callback:
            self.output_char_callback(ch)
        else:
            # Fallback: agregar a buffer
            try:
                self.output_buffer += chr(ch)
            except Exception:
                self.output_buffer += f"[0x{ch:02X}]"

    def _write_int(self, value: int):
        """Escribe un entero"""
        val = int(value & 0xFFFFFFFFFFFFFFFF)

        if self.output_int_callback:
            self.output_int_callback(val)
        else:
            # Fallback: agregar a buffer
            self.output_int_buffer.append(val)

    def _output_int_no_newline(self, value: int):
        """Escribe entero sin newline (para formato)"""
        val = int(value & 0xFFFFFFFFFFFFFFFF)

        if self.output_int_callback:
            # La GUI decide cómo manejarlo
            self.output_int_callback(val)
        else:
            # Fallback: convertir a string y agregar
            self.output_buffer += str(val)

    def _output_int_array(self, base_addr: int, count: int, separator: int):
        """
        Imprime array de enteros con separador

        Args:
            base_addr: Dirección base del array
            count: Número de elementos
            separator: Carácter ASCII separador
        """
        count = max(0, min(count, 1_000_000))  # Límite de seguridad

        for i in range(count):
            addr = base_addr + i * 8
            if not (0 <= addr <= (self.memory_size - 8)):
                break

            val = self.mem.read_word(addr)
            self._output_int_no_newline(val)

            # Separador entre números (no después del último)
            if i != count - 1 and separator:
                self._write_char(separator)

    # === Entrada (IN) ===

    def read_input(self, source: int, func: int) -> int:
        """
        Maneja instrucción IN

        Args:
            source: Puerto o dirección MMIO
            func: Campo FUNC (determina modo)

        Returns:
            Valor de 64 bits leído
        """
        mode_port = func & 1

        if mode_port == 1:
            # Entrada desde puerto numérico
            return self._input_from_port(source)
        else:
            # Entrada desde dirección MMIO
            return self._input_from_mmio(source)

    def _input_from_port(self, port: int) -> int:
        """Lee desde puerto numérico"""
        if port == 1:
            return self._read_char()
        elif port == 2:
            return self._read_int()
        else:
            # Puerto desconocido
            return 0

    def _input_from_mmio(self, address: int) -> int:
        """Lee desde dirección MMIO"""
        if address == self.MMIO_CONSOLE_IN_CHAR:
            return self._read_char()
        elif address == self.MMIO_CONSOLE_IN_INT:
            return self._read_int()
        else:
            # MMIO genérico: leer como memoria si está en rango
            if 0 <= address <= (self.memory_size - 8):
                return self.mem.read_word(address)
            return 0

    def _read_char(self) -> int:
        """Lee un carácter desde la entrada"""
        if self.input_char_callback:
            return self.input_char_callback() & 0xFF

        # Fallback: retornar 0
        return 0

    def _read_int(self) -> int:
        """Lee un entero desde la entrada"""
        if self.input_int_callback:
            return self.input_int_callback() & 0xFFFFFFFFFFFFFFFF

        # Fallback: retornar 0
        return 0

    # === Configuración de callbacks (para la GUI) ===

    def set_output_char_callback(self, callback: Callable[[int], None]):
        """Registra callback para salida de caracteres"""
        self.output_char_callback = callback

    def set_output_int_callback(self, callback: Callable[[int], None]):
        """Registra callback para salida de enteros"""
        self.output_int_callback = callback

    def set_input_char_callback(self, callback: Callable[[], int]):
        """Registra callback para entrada de caracteres"""
        self.input_char_callback = callback

    def set_input_int_callback(self, callback: Callable[[], int]):
        """Registra callback para entrada de enteros"""
        self.input_int_callback = callback

    # === Utilidades ===

    def get_output_buffer(self) -> str:
        """Obtiene y limpia el buffer de salida de caracteres"""
        output = self.output_buffer
        self.output_buffer = ""
        return output

    def get_output_int_buffer(self) -> list:
        """Obtiene y limpia el buffer de salida de enteros"""
        output = self.output_int_buffer.copy()
        self.output_int_buffer = []
        return output

    def clear_buffers(self):
        """Limpia todos los buffers de salida"""
        self.output_buffer = ""
        self.output_int_buffer = []

    # === Operaciones de Strings ===

    def read_string(self, port: int, max_length: int = 1000) -> str:
        """
        Lee un string desde un puerto

        Args:
            port: Puerto de entrada
                - 0xFFFF0018: Consola (stdin)
                - 0xFFFF0020: Archivo (debe estar abierto previamente)
            max_length: Longitud máxima del string

        Returns:
            String leído
        """
        # Puerto de consola
        if port == self.MMIO_CONSOLE_IN_INT or port == 0xFFFF0018:
            return self._read_string_from_console(max_length)

        # Puerto de archivo
        elif port in self.open_files:
            return self._read_string_from_file(port, max_length)

        # Puerto desconocido
        return ""

    def write_string(self, text: str, port: int):
        """
        Escribe un string a un puerto

        Args:
            text: String a escribir
            port: Puerto de salida
                - 0xFFFF0008: Consola (stdout)
                - 0xFFFF0020: Archivo (debe estar abierto previamente)
        """
        # Puerto de consola
        if port == self.MMIO_CONSOLE_INT or port == 0xFFFF0008:
            self._write_string_to_console(text)

        # Puerto de archivo
        elif port in self.open_files:
            self._write_string_to_file(text, port)

    def read_string_from_memory(self, base_addr: int, max_length: int = 1000) -> str:
        """
        Lee un string null-terminated desde memoria

        Args:
            base_addr: Dirección de inicio del string
            max_length: Longitud máxima (seguridad)

        Returns:
            String leído
        """
        chars = []
        offset = 0

        while offset < max_length:
            addr = base_addr + offset
            if addr >= self.memory_size:
                break

            byte_val = self.mem.read_byte(addr)
            if byte_val == 0:  # Null terminator
                break

            chars.append(chr(byte_val))
            offset += 1

        return "".join(chars)

    def write_string_to_memory(self, base_addr: int, text: str, max_length: int = 1000):
        """
        Escribe un string null-terminated en memoria

        Args:
            base_addr: Dirección de inicio
            text: String a escribir
            max_length: Longitud máxima (seguridad)
        """
        text_to_write = text[:max_length]  # Limitar longitud

        for i, ch in enumerate(text_to_write):
            addr = base_addr + i
            if addr >= self.memory_size:
                break
            self.mem.write_byte(addr, ord(ch) & 0xFF)

        # Agregar null terminator
        terminator_addr = base_addr + len(text_to_write)
        if terminator_addr < self.memory_size:
            self.mem.write_byte(terminator_addr, 0)

    # === Helpers de consola ===

    def _read_string_from_console(self, max_length: int) -> str:
        """Lee string desde consola usando callback"""
        if self.input_char_callback:
            chars = []
            for _ in range(max_length):
                ch = self.input_char_callback()
                if ch == 0 or ch == 10:  # Null o newline
                    break
                chars.append(chr(ch & 0xFF))
            return "".join(chars)
        return ""

    def _write_string_to_console(self, text: str):
        """Escribe string a consola usando callback"""
        if self.output_char_callback:
            for ch in text:
                self.output_char_callback(ord(ch))
        else:
            self.output_buffer += text

    # === Helpers de archivo ===

    def _read_string_from_file(self, port: int, max_length: int) -> str:
        """Lee string desde archivo"""
        try:
            file_handle = self.open_files.get(port)
            if file_handle:
                return file_handle.readline(max_length).rstrip("\n\r")
        except Exception:
            pass
        return ""

    def _write_string_to_file(self, text: str, port: int):
        """Escribe string a archivo"""
        try:
            file_handle = self.open_files.get(port)
            if file_handle:
                file_handle.write(text)
                file_handle.flush()  # Forzar escritura inmediata
        except Exception:
            pass

    # === Gestión de archivos ===

    def open_file(self, port: int, filepath: str, mode: str = "r"):
        """
        Abre un archivo y lo asocia a un puerto

        Args:
            port: Número de puerto (ej: 0xFFFF0020)
            filepath: Ruta del archivo
            mode: Modo de apertura ('r', 'w', 'a', etc.)
        """
        try:
            self.open_files[port] = open(filepath, mode, encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"No se pudo abrir archivo {filepath}: {e}")

    def close_file(self, port: int):
        """
        Cierra un archivo asociado a un puerto

        Args:
            port: Número de puerto
        """
        if port in self.open_files:
            try:
                self.open_files[port].close()
            except Exception:
                pass
            finally:
                del self.open_files[port]

    def close_all_files(self):
        """Cierra todos los archivos abiertos"""
        for port in list(self.open_files.keys()):
            self.close_file(port)
