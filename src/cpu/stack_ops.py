"""
Módulo de operaciones de pila para la CPU
"""

from src.memory.memory import Memory


class StackOperations:
    """Maneja operaciones de pila (PUSH/POP) para la CPU"""

    def __init__(self, memory: Memory, memory_size: int):
        """
        Inicializa operaciones de pila

        Args:
            memory: Objeto Memory
            memory_size: Tamaño total de la memoria
        """
        self.mem = memory
        self.memory_size = memory_size
        self.stack_pointer: int = memory_size  # Comienza en el tope (crece hacia abajo)

    def push(self, value: int):
        """
        Empuja un valor de 64 bits a la pila

        La pila crece hacia abajo (decrementa SP antes de escribir)

        Args:
            value: Valor de 64 bits a empujar

        Raises:
            RuntimeError: Si hay stack overflow
        """
        if self.stack_pointer < 8:
            raise RuntimeError(
                f"Stack overflow: SP=0x{self.stack_pointer:08X}, no hay espacio"
            )

        # Decrementar stack pointer (pila crece hacia abajo)
        self.stack_pointer -= 8

        # Escribir valor en la pila
        self.mem.write_word(self.stack_pointer, value & 0xFFFFFFFFFFFFFFFF)

    def pop(self) -> int:
        """
        Saca un valor de 64 bits de la pila

        Args:
            None

        Returns:
            Valor de 64 bits sacado de la pila

        Raises:
            RuntimeError: Si hay stack underflow
        """
        if self.stack_pointer >= self.memory_size:
            raise RuntimeError(
                f"Stack underflow: SP=0x{self.stack_pointer:08X}, "
                f"memoria_max=0x{self.memory_size:08X}"
            )

        # Leer valor de la pila
        value = self.mem.read_word(self.stack_pointer)

        # Incrementar stack pointer (volver hacia arriba)
        self.stack_pointer += 8

        return value

    def peek(self, offset: int = 0) -> int:
        """
        Lee un valor de la pila sin sacarlo

        Args:
            offset: Offset en palabras (0 = tope, 1 = siguiente, etc.)

        Returns:
            Valor de 64 bits en la posición especificada
        """
        address = self.stack_pointer + (offset * 8)

        if address < 0 or address >= self.memory_size:
            raise RuntimeError(f"Peek fuera de rango: dirección=0x{address:08X}")

        return self.mem.read_word(address)

    def reset(self):
        """Reinicia el stack pointer al tope de la memoria"""
        self.stack_pointer = self.memory_size

    def get_depth(self) -> int:
        """
        Calcula la profundidad actual de la pila en palabras

        Returns:
            Número de palabras (64 bits) en la pila
        """
        return (self.memory_size - self.stack_pointer) // 8

    def is_empty(self) -> bool:
        """
        Verifica si la pila está vacía

        Returns:
            True si la pila está vacía
        """
        return self.stack_pointer >= self.memory_size

    def get_used_space(self) -> int:
        """
        Calcula el espacio usado por la pila en bytes

        Returns:
            Bytes usados por la pila
        """
        return self.memory_size - self.stack_pointer

    def get_available_space(self) -> int:
        """
        Calcula el espacio disponible para la pila en bytes

        Returns:
            Bytes disponibles
        """
        return self.stack_pointer
