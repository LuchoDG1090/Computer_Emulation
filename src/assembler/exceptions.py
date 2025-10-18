"""Excepciones personalizadas para el ensamblador"""


class AssemblerError(Exception):
    """Excepción base para errores del ensamblador"""

    pass


class LexerError(AssemblerError):
    """Error durante el análisis léxico"""

    pass


class ParserError(AssemblerError):
    """Error durante el parseo"""

    pass


class SymbolError(AssemblerError):
    """Error relacionado con símbolos/etiquetas"""

    pass


class EncodingError(AssemblerError):
    """Error durante la codificación de instrucciones"""

    pass
