from enum import IntEnum


# Operaciones de las instrucciones
class Opcodes(IntEnum):
    """Codigos de operacion para las instrucciones"""

    # Instrucciones ALU
    ADD = 0x10  # Suma
    SUB = 0x11  # Resta
    MUL = 0x12  # Multiplicacion
    DIV = 0x13  # Division
    AND = 0x14  # AND logico
    OR = 0x15  # OR logico
    XOR = 0x16  # XOR logico
    NOT = 0x17  # NOT logico
    SHL = 0x18  # Desplazamiento izquierda
    SHR = 0x19  # Desplazamiento derecha

    # Instrucciones de punto flotante (IEEE 754 double precision)
    FADD = 0x1A  # Suma flotante
    FSUB = 0x1B  # Resta flotante
    FMUL = 0x1C  # Multiplicación flotante
    FDIV = 0x1D  # División flotante

    # Instrucciones ALU con inmediato
    ADDI = 0x20  # Suma con inmediato
    MOVI = 0x22  # Mover inmediato a registro
    LD = 0x23  # Cargar desde memoria
    ST = 0x24  # Almacenar en memoria
    CP = 0x29  # Copiar registro a registro

    # Instrucciones de comparación
    CMP = 0x30  # Comparación

    # Instrucciones de control de flujo
    JMP = 0x40  # Salto incondicional
    JZ = 0x41  # Salto si cero
    JNZ = 0x42  # Salto si no cero
    JC = 0x43  # Salto si carry
    JNC = 0x44  # Salto si no carry
    JS = 0x45  # Salto si negativo (signed)
    CALL = 0x46  # Llamada a subrutina
    RET = 0x47  # Retorno de subrutina

    # Instrucciones de transferencia de datos
    PUSH = 0x50  # Empujar a pila
    POP = 0x51  # Sacar de pila

    # Instrucciones de entrada/salida
    IN = 0x60  # Entrada desde MMIO/puerto
    OUT = 0x61  # Salida a MMIO/puerto
    INS = 0x62  # Entrada de bloque
    OUTS = 0x63  # Salida de bloque

    # Instrucciones de sistema
    NOP = 0x70  # No operacion
    HALT = 0x71  # Detener CPU


# Tipos de instrucciones
class InstructionType(IntEnum):
    """Tipos de instruccion"""

    R_TYPE = 0  # Registro-Registro (operaciones ALU entre registros)
    I_TYPE = 1  # Inmediato/Direccion (operaciones con inmediatos, LOAD/STORE)
    J_TYPE = 2  # Salto/Llamada (JMP, CALL, saltos condicionales)
    S_TYPE = 3  # Sistema/Efecto (HALT, NOP, operaciones especiales)


# Mapeo de opcodes a tipos de instruccion
opcode_to_type = {
    # R-Type: operaciones ALU entre registros
    Opcodes.ADD: InstructionType.R_TYPE,
    Opcodes.SUB: InstructionType.R_TYPE,
    Opcodes.MUL: InstructionType.R_TYPE,
    Opcodes.DIV: InstructionType.R_TYPE,
    Opcodes.AND: InstructionType.R_TYPE,
    Opcodes.OR: InstructionType.R_TYPE,
    Opcodes.XOR: InstructionType.R_TYPE,
    Opcodes.NOT: InstructionType.R_TYPE,
    Opcodes.SHL: InstructionType.R_TYPE,
    Opcodes.SHR: InstructionType.R_TYPE,
    Opcodes.CMP: InstructionType.R_TYPE,
    # Operaciones flotantes (también R-Type)
    Opcodes.FADD: InstructionType.R_TYPE,
    Opcodes.FSUB: InstructionType.R_TYPE,
    Opcodes.FMUL: InstructionType.R_TYPE,
    Opcodes.FDIV: InstructionType.R_TYPE,
    # I-Type: operaciones con inmediatos y memoria
    Opcodes.MOVI: InstructionType.I_TYPE,
    Opcodes.CP: InstructionType.I_TYPE,
    Opcodes.LD: InstructionType.I_TYPE,
    Opcodes.ST: InstructionType.I_TYPE,
    Opcodes.PUSH: InstructionType.I_TYPE,
    Opcodes.POP: InstructionType.I_TYPE,
    Opcodes.ADDI: InstructionType.I_TYPE,
    Opcodes.OUT: InstructionType.I_TYPE,
    Opcodes.IN: InstructionType.I_TYPE,
    Opcodes.INS: InstructionType.I_TYPE,
    Opcodes.OUTS: InstructionType.I_TYPE,
    # J-Type: saltos y llamadas
    Opcodes.JMP: InstructionType.J_TYPE,
    Opcodes.JZ: InstructionType.J_TYPE,
    Opcodes.JNZ: InstructionType.J_TYPE,
    Opcodes.JC: InstructionType.J_TYPE,
    Opcodes.JNC: InstructionType.J_TYPE,
    Opcodes.JS: InstructionType.J_TYPE,
    Opcodes.CALL: InstructionType.J_TYPE,
    Opcodes.RET: InstructionType.J_TYPE,
    # S-Type: sistema
    Opcodes.HALT: InstructionType.S_TYPE,
    Opcodes.NOP: InstructionType.S_TYPE,
}


def get_all_instruction_names():
    """Devuelve una lista con los nombres de todas las instrucciones"""
    return [opcode.name for opcode in Opcodes]


def get_instruction_type(opcode_name):
    """
    Obtiene el tipo de instrucción dado su nombre

    Args:
        opcode_name (str): Nombre de la instrucción (ej: 'ADD', 'MOVI')

    Returns:
        InstructionType: Tipo de instrucción (R_TYPE, I_TYPE, etc.)
    """
    try:
        opcode = Opcodes[opcode_name]
        return opcode_to_type.get(opcode)
    except KeyError:
        return None


def get_opcode_value(opcode_name):
    """
    Obtiene el valor hexadecimal del opcode

    Args:
        opcode_name (str): Nombre de la instrucción

    Returns:
        int: Valor del opcode
    """
    try:
        return Opcodes[opcode_name].value
    except KeyError:
        return None


def is_valid_instruction(opcode_name):
    """Verifica si una instrucción es válida"""
    try:
        Opcodes[opcode_name]
        return True
    except KeyError:
        return False


# Diccionario para uso directo en el lexer
INSTRUCTION_NAMES = {name: "OPCODE" for name in get_all_instruction_names()}
