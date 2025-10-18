"""Tabla de símbolos para etiquetas"""

from src.assembler.exceptions import SymbolError


class SymbolTable:
    """Maneja etiquetas y sus direcciones"""

    def __init__(self):
        self.symbols = {}

    def add(self, label, address):
        """
        Agrega una etiqueta a la tabla

        Args:
            label (str): Nombre de la etiqueta
            address (int): Dirección de memoria

        Raises:
            SymbolError: Si la etiqueta ya existe
        """
        if label in self.symbols:
            raise SymbolError(f"Etiqueta duplicada: {label}")
        self.symbols[label] = address

    def get(self, label):
        """
        Obtiene la dirección de una etiqueta

        Args:
            label (str): Nombre de la etiqueta

        Returns:
            int: Dirección de memoria

        Raises:
            SymbolError: Si la etiqueta no existe
        """
        if label not in self.symbols:
            raise SymbolError(f"Etiqueta no definida: {label}")
        return self.symbols[label]

    def exists(self, label):
        """Verifica si una etiqueta existe"""
        return label in self.symbols

    def clear(self):
        """Limpia la tabla de símbolos"""
        self.symbols.clear()

    def get_all(self):
        """Retorna todas las etiquetas"""
        return dict(self.symbols)
