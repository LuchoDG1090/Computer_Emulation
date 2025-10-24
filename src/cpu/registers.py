"""
Módulo de gestión de registros de propósito general
"""

from typing import List


class RegisterFile:
    """Banco de registros de propósito general (R0-R15)"""

    def __init__(self):
        """Inicializa 16 registros de 64 bits"""
        self._registers: List[int] = [0] * 16

    def read(self, reg_num: int) -> int:
        """
        Lee el valor de un registro

        Args:
            reg_num: Número de registro (0-15)

        Returns:
            Valor del registro (64 bits)
        """
        if not 0 <= reg_num <= 15:
            raise ValueError(f"Registro inválido: {reg_num} (debe ser 0-15)")

        return self._registers[reg_num]

    def write(self, reg_num: int, value: int):
        """
        Escribe un valor en un registro

        Args:
            reg_num: Número de registro (0-15)
            value: Valor a escribir (se trunca a 64 bits)
        """
        if not 0 <= reg_num <= 15:
            raise ValueError(f"Registro inválido: {reg_num} (debe ser 0-15)")

        # Mantener solo 64 bits
        self._registers[reg_num] = value & 0xFFFFFFFFFFFFFFFF

    def get_all(self) -> List[int]:
        """
        Retorna una copia de todos los registros

        Returns:
            Lista con los valores de R0-R15
        """
        return self._registers.copy()

    def reset(self):
        """Reinicia todos los registros a 0"""
        self._registers = [0] * 16

    def __getitem__(self, reg_num: int) -> int:
        """Permite acceso con notación de índice: registers[5]"""
        return self.read(reg_num)

    def __setitem__(self, reg_num: int, value: int):
        """Permite asignación con notación de índice: registers[5] = 100"""
        self.write(reg_num, value)

    def __repr__(self) -> str:
        """Representación legible de los registros"""
        lines = ["RegisterFile:"]
        for i in range(16):
            lines.append(f"  R{i:2d}: 0x{self._registers[i]:016X}")
        return "\n".join(lines)
