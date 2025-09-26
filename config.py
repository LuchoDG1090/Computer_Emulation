"""
Configuración del Emulador de CPU

Este archivo contiene configuraciones y constantes globales
para el emulador de CPU.
"""

# Configuración de memoria
DEFAULT_MEMORY_SIZE = 65536  # 64KB por defecto
MAX_MEMORY_SIZE = 1048576    # 1MB máximo

# Configuración de ejecución
MAX_CYCLES_DEFAULT = 10000   # Máximo de ciclos por defecto para evitar bucles infinitos
STACK_GROWTH_DIRECTION = -1  # -1 para crecimiento hacia abajo, 1 hacia arriba

# Configuración de debug
DEBUG_MODE = False           # Activar/desactivar modo debug
VERBOSE_EXECUTION = False    # Mostrar cada instrucción ejecutada

# Configuración de rendimiento
ENABLE_CYCLE_COUNTING = True # Contar ciclos de CPU
ENABLE_PROFILING = False     # Activar profiling de rendimiento

# Valores por defecto de registros
INITIAL_PC = 0              # Valor inicial del Program Counter
INITIAL_SP_OFFSET = -1      # Offset del Stack Pointer desde el final de memoria

# Códigos de error
ERROR_CODES = {
    'INVALID_OPCODE': 1,
    'MEMORY_ACCESS_VIOLATION': 2,
    'STACK_OVERFLOW': 3,
    'STACK_UNDERFLOW': 4,
    'DIVISION_BY_ZERO': 5,
    'INVALID_REGISTER': 6,
    'INVALID_ADDRESSING_MODE': 7,
    'PC_OUT_OF_BOUNDS': 8
}

# Configuración de formato de salida
OUTPUT_FORMAT = {
    'hex_digits': 16,        # Número de dígitos hexadecimales a mostrar
    'show_leading_zeros': True,
    'uppercase_hex': True
}

# Límites de la arquitectura
ARCHITECTURE_LIMITS = {
    'instruction_size': 64,   # bits
    'word_size': 64,         # bits
    'max_operand_size': 24,  # bits
    'num_general_registers': 16,
    'flag_register_size': 8, # bits
    'max_shift_amount': 63   # bits
}