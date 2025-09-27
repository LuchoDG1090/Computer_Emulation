from enum import IntEnum

# Operaciones de las instrucciones
class Opcodes(IntEnum):
    """Codigos de operacion para las instrucciones"""
    # Instrucciones ALU
    ADD = 0x01      # Suma
    SUB = 0x02      # Resta
    MUL = 0x03      # Multiplicacion
    DIV = 0x04      # Division
    AND = 0x05      # AND logico
    OR = 0x06       # OR logico
    XOR = 0x07      # XOR logico
    NOT = 0x08      # NOT logico
    SHL = 0x09      # Desplazamiento izquierda
    SHR = 0x0A      # Desplazamiento derecha
    CMP = 0x0B      # Comparacion
    
    # Instrucciones de transferencia de datos
    MOV = 0x10      # Mover datos
    LOAD = 0x11     # Cargar desde memoria
    STORE = 0x12    # Almacenar en memoria
    PUSH = 0x13     # Empujar a pila
    POP = 0x14      # Sacar de pila
    
    # Instrucciones de control de flujo
    JMP = 0x20      # Salto incondicional
    JZ = 0x21       # Salto si cero
    JNZ = 0x22      # Salto si no cero
    JC = 0x23       # Salto si carry
    JNC = 0x24      # Salto si no carry
    CALL = 0x25     # Llamada a subrutina
    RET = 0x26      # Retorno de subrutina
    
    # Instrucciones de sistema
    HALT = 0xFF     # Detener CPU
    NOP = 0x00      # No operacion

# Tipos de instrucciones
class InstructionType(IntEnum):
    """Tipos de instruccion"""
    R_TYPE = 0      # Registro-Registro (operaciones ALU entre registros)
    I_TYPE = 1      # Inmediato/Direccion (operaciones con inmediatos, LOAD/STORE)
    J_TYPE = 2      # Salto/Llamada (JMP, CALL, saltos condicionales)
    S_TYPE = 3      # Sistema/Efecto (HALT, NOP, operaciones especiales)

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
    
    # I-Type: operaciones con inmediatos y memoria
    Opcodes.MOV: InstructionType.I_TYPE,
    Opcodes.LOAD: InstructionType.I_TYPE,
    Opcodes.STORE: InstructionType.I_TYPE,
    Opcodes.PUSH: InstructionType.I_TYPE,
    Opcodes.POP: InstructionType.I_TYPE,
    
    # J-Type: saltos y llamadas
    Opcodes.JMP: InstructionType.J_TYPE,
    Opcodes.JZ: InstructionType.J_TYPE,
    Opcodes.JNZ: InstructionType.J_TYPE,
    Opcodes.JC: InstructionType.J_TYPE,
    Opcodes.JNC: InstructionType.J_TYPE,
    Opcodes.CALL: InstructionType.J_TYPE,
    Opcodes.RET: InstructionType.J_TYPE,
    
    # S-Type: sistema
    Opcodes.HALT: InstructionType.S_TYPE,
    Opcodes.NOP: InstructionType.S_TYPE,
}