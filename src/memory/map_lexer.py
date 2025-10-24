"""
Lexer para archivos .map usando PLY
"""

import src.ply.lex as lex
import src.user_interface.logging.logger as logger

logger_handler = logger.configurar_logger()


class MapLexer:
    """Lexer para archivos .map usando PLY"""

    tokens = ("NUMBER", "HEX", "NEWLINE")

    t_ignore = " \t,"

    def t_HEX(self, t):
        r"0x[0-9A-Fa-f]+"
        t.value = int(t.value, 16)
        return t

    def t_NUMBER(self, t):
        r"\d+"
        t.value = int(t.value)
        return t

    def t_NEWLINE(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)
        return t

    def t_COMMENT(self, t):
        r"\#.*"
        pass

    def t_error(self, t):
        logger_handler.error(
            f"Carácter ilegal '{t.value[0]}' en línea {t.lexer.lineno}"
        )
        t.lexer.skip(1)

    def build(self):
        """Construye el lexer"""
        self.lexer = lex.lex(module=self)
        return self.lexer
