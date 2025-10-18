"""Analizador léxico usando PLY"""

import src.ply.lex as lex
from src.assembler.exceptions import LexerError
from src.isa.isa import Opcodes

# Lista de nombres de todas las instrucciones válidas
INSTRUCTION_NAMES = [opcode.name for opcode in Opcodes]

# Palabras reservadas
reserved = {name: "OPCODE" for name in INSTRUCTION_NAMES}

# Agregar directivas
reserved.update(
    {
        "ORG": "DIRECTIVE",
        "DW": "DIRECTIVE",
        "RESW": "DIRECTIVE",
    }
)

# Tokens
tokens = (
    "OPCODE",
    "DIRECTIVE",
    "REGISTER",
    "IMMEDIATE",
    "LABEL",
    "COMMA",
    "NEWLINE",
    "LBRACKET",
    "RBRACKET",
    "IDENTIFIER",
)

# Expresiones regulares para tokens simples
t_COMMA = r","
t_LBRACKET = r"\["
t_RBRACKET = r"\]"


def t_LABEL(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*:"
    t.value = t.value[:-1]  # Remover ':'
    return t


def t_REGISTER(t):
    r"R(1[0-5]|[0-9])"
    t.value = int(t.value[1:])  # Extraer número del registro
    return t


def t_OPCODE(t):
    r"[A-Z][A-Z0-9_]*"
    t.type = reserved.get(t.value, "OPCODE")
    return t


def t_IDENTIFIER(t):
    r"[a-z_][a-z_0-9]*"
    return t


def t_IMMEDIATE(t):
    r"(-?0x[0-9A-Fa-f]+)|(-?\d+)"
    if t.value.startswith("0x") or t.value.startswith("-0x"):
        t.value = int(t.value, 16)
    else:
        t.value = int(t.value)
    return t


def t_COMMENT(t):
    r"\#.*"
    pass  # Ignorar comentarios


def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    return t


# Caracteres ignorados (espacios y tabs)
t_ignore = " \t"


def t_error(t):
    raise LexerError(f"Caracter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")


# Construir el lexer
lexer = lex.lex()
