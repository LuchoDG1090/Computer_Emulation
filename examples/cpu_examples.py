"""
Ejemplos de uso de la CPU Emulada

Este archivo contiene varios ejemplos que demuestran las capacidades
de la CPU implementada, incluyendo diferentes tipos de instrucciones
y programas mas complejos.
"""

import struct
import sys
import os

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cpu.cpu import (
    CPU, InstructionDecoder, Opcodes, AddressingMode, InstructionType, Flags
)


def example_basic_arithmetic():
    """Ejemplo basico de operaciones aritmeticas"""
    print("=== EJEMPLO: OPERACIONES ARITMeTICAS BaSICAS ===")
    
    cpu = CPU()
    decoder = InstructionDecoder()
    instructions = []
    
    # Programa: Calcular (15 + 25) * 2 - 10
    print("Programa: (15 + 25) * 2 - 10")
    print("Instrucciones:")
    
    # MOV R0, #15 (I-Type)
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=0, rs1=0, imm32=15, func=0
    ))
    print("1. MOV R0, #15         ; I-Type: cargar inmediato")
    
    # MOV R1, #25 (I-Type)
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=1, rs1=0, imm32=25, func=0
    ))
    print("2. MOV R1, #25         ; I-Type: cargar inmediato")
    
    # ADD R0, R0, R1 (R-Type: R0 = R0 + R1 = 40)
    instructions.append(decoder.encode_r_type(
        Opcodes.ADD, rd=0, rs1=0, rs2=1, func=0
    ))
    print("3. ADD R0, R0, R1      ; R-Type: R0 = R0 + R1")
    
    # MOV R2, #2 (I-Type)
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=2, rs1=0, imm32=2, func=0
    ))
    print("4. MOV R2, #2          ; I-Type: cargar inmediato")
    
    # MUL R0, R0, R2 (R-Type: R0 = R0 * R2 = 80)
    instructions.append(decoder.encode_r_type(
        Opcodes.MUL, rd=0, rs1=0, rs2=2, func=0
    ))
    print("5. MUL R0, R0, R2      ; R-Type: R0 = R0 * R2")
    
    # MOV R3, #10 (I-Type)
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=3, rs1=0, imm32=10, func=0
    ))
    print("6. MOV R3, #10         ; I-Type: cargar inmediato")
    
    # SUB R0, R0, R3 (R-Type: R0 = R0 - R3 = 70)
    instructions.append(decoder.encode_r_type(
        Opcodes.SUB, rd=0, rs1=0, rs2=3, func=0
    ))
    print("7. SUB R0, R0, R3      ; R-Type: R0 = R0 - R3")
    
    # HALT (S-Type)
    instructions.append(decoder.encode_s_type(Opcodes.HALT))
    print("8. HALT                ; S-Type: detener CPU")
    
    # Ejecutar programa
    program = bytearray()
    for inst in instructions:
        program.extend(struct.pack('<Q', inst))
    
    cpu.load_program(bytes(program))
    print("\nEjecutando...")
    cpu.run()
    
    print(f"\nResultado: R0 = {cpu.registers[0]} (esperado: 70)")
    print(f"Ciclos ejecutados: {cpu.cycle_count}")
    print()


def example_logical_operations():
    """Ejemplo de operaciones logicas"""
    print("=== EJEMPLO: OPERACIONES LoGICAS ===")
    
    cpu = CPU()
    decoder = InstructionDecoder()
    instructions = []
    
    print("Programa: Operaciones AND, OR, XOR con 0xFF y 0xF0")
    print("Instrucciones:")
    
    # MOV R0, #0xFF - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=0, rs1=0, imm32=0xFF, func=0
    ))
    print("1. MOV R0, #0xFF       ; I-Type: cargar inmediato")
    
    # MOV R1, #0xF0 - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=1, rs1=0, imm32=0xF0, func=0
    ))
    print("2. MOV R1, #0xF0       ; I-Type: cargar inmediato")
    
    # AND R2, R0, R1 - R-Type
    instructions.append(decoder.encode_r_type(
        Opcodes.AND, rd=2, rs1=0, rs2=1, func=0
    ))
    print("3. AND R2, R0, R1      ; R-Type: R2 = R0 & R1")
    
    # OR R3, R0, R1 - R-Type
    instructions.append(decoder.encode_r_type(
        Opcodes.OR, rd=3, rs1=0, rs2=1, func=0
    ))
    print("4. OR R3, R0, R1       ; R-Type: R3 = R0 | R1")
    
    # XOR R4, R0, R1 - R-Type
    instructions.append(decoder.encode_r_type(
        Opcodes.XOR, rd=4, rs1=0, rs2=1, func=0
    ))
    print("5. XOR R4, R0, R1      ; R-Type: R4 = R0 ^ R1")
    
    # HALT - S-Type
    instructions.append(decoder.encode_s_type(Opcodes.HALT))
    print("6. HALT                ; S-Type: detener CPU")
    
    # Ejecutar
    program = bytearray()
    for inst in instructions:
        program.extend(struct.pack('<Q', inst))
    
    cpu.load_program(bytes(program))
    print("\nEjecutando...")
    cpu.run()
    
    print(f"\nResultados:")
    print(f"R0 (0xFF): 0x{cpu.registers[0]:X}")
    print(f"R1 (0xF0): 0x{cpu.registers[1]:X}")
    print(f"R2 (AND): 0x{cpu.registers[2]:X} (esperado: 0xF0)")
    print(f"R3 (OR):  0x{cpu.registers[3]:X} (esperado: 0xFF)")
    print(f"R4 (XOR): 0x{cpu.registers[4]:X} (esperado: 0xF)")
    print()


def example_conditional_jumps():
    """Ejemplo de saltos condicionales"""
    print("=== EJEMPLO: SALTOS CONDICIONALES ===")
    
    cpu = CPU()
    decoder = InstructionDecoder()
    instructions = []
    
    print("Programa: Encontrar el maximo entre dos numeros")
    print("Instrucciones:")
    
    # MOV R0, #25  (primer numero) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=0, rs1=0, imm32=25, func=0
    ))
    print("1. MOV R0, #25         ; I-Type: cargar primer numero")
    
    # MOV R1, #30  (segundo numero) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=1, rs1=0, imm32=30, func=0
    ))
    print("2. MOV R1, #30         ; I-Type: cargar segundo numero")
    
    # CMP R0, R1 - R-Type
    instructions.append(decoder.encode_r_type(
        Opcodes.CMP, rd=0, rs1=0, rs2=1, func=0
    ))
    print("3. CMP R0, R1          ; R-Type: comparar R0 con R1")
    
    # Si R0 >= R1, saltar a FIRST_IS_MAX - J-Type
    first_max_addr = 8 * 6  # Direccion de la instruccion 7 (FIRST_IS_MAX)
    instructions.append(decoder.encode_j_type(
        Opcodes.JNC, first_max_addr, func=0
    ))
    print("4. JNC FIRST_IS_MAX    ; J-Type: saltar si no carry (R0 >= R1)")
    
    # R1 es el maximo: MOV R2, R1 - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=2, rs1=1, imm32=0, func=1  # func=1 para registro a registro
    ))
    print("5. MOV R2, R1          ; I-Type: R2 = R1 (R1 es el maximo)")
    
    # Saltar al final - J-Type
    end_addr = 8 * 7  # Direccion de HALT
    instructions.append(decoder.encode_j_type(
        Opcodes.JMP, end_addr, func=0
    ))
    print("6. JMP END             ; J-Type: saltar al final")
    
    # FIRST_IS_MAX: MOV R2, R0 - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=2, rs1=0, imm32=0, func=1  # func=1 para registro a registro
    ))
    print("7. FIRST_IS_MAX: MOV R2, R0 ; I-Type: R2 = R0 (R0 es el maximo)")
    
    # END: HALT - S-Type
    instructions.append(decoder.encode_s_type(Opcodes.HALT))
    print("8. END: HALT           ; S-Type: detener CPU")
    
    # Ejecutar
    program = bytearray()
    for inst in instructions:
        program.extend(struct.pack('<Q', inst))
    
    cpu.load_program(bytes(program))
    print("\nEjecutando...")
    cpu.run()
    
    print(f"\nResultados:")
    print(f"Primer numero (R0): {cpu.registers[0]}")
    print(f"Segundo numero (R1): {cpu.registers[1]}")
    print(f"Maximo (R2): {cpu.registers[2]} (esperado: 30)")
    print()


def example_subroutine_call():
    """Ejemplo de llamada a subrutina"""
    print("=== EJEMPLO: LLAMADA A SUBRUTINA ===")
    
    cpu = CPU()
    decoder = InstructionDecoder()
    instructions = []
    
    print("Programa: Subrutina para calcular factorial de 4")
    print("Instrucciones:")
    
    # Programa principal
    # MOV R0, #4  (calcular factorial de 4) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=0, rs1=0, imm32=4, func=0
    ))
    print("1. MOV R0, #4          ; I-Type: numero para factorial")
    
    # CALL FACTORIAL - J-Type
    factorial_addr = 8 * 4  # Direccion de la subrutina
    instructions.append(decoder.encode_j_type(
        Opcodes.CALL, factorial_addr, func=0
    ))
    print("2. CALL FACTORIAL      ; J-Type: llamar subrutina")
    
    # MOV R2, R1  (guardar resultado) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=2, rs1=1, imm32=0, func=1  # func=1 para registro a registro
    ))
    print("3. MOV R2, R1          ; I-Type: guardar resultado")
    
    # HALT - S-Type
    instructions.append(decoder.encode_s_type(Opcodes.HALT))
    print("4. HALT                ; S-Type: detener CPU")
    
    # Subrutina FACTORIAL (entrada: R0, salida: R1)
    print("\nSubrutina FACTORIAL:")
    
    # MOV R1, #1  (inicializar resultado) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=1, rs1=0, imm32=1, func=0
    ))
    print("5. MOV R1, #1          ; I-Type: inicializar resultado")
    
    # LOOP: CMP R0, #0 - R-Type (comparar R0 con 0 usando registro R15 como 0)
    loop_addr = 8 * 5  # Direccion actual del LOOP
    # Primero cargar 0 en un registro temporal
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=15, rs1=0, imm32=0, func=0  # R15 = 0
    ))
    instructions.append(decoder.encode_r_type(
        Opcodes.CMP, rd=0, rs1=0, rs2=15, func=0  # CMP R0, R15 (que es 0)
    ))
    print("6. MOV R15, #0         ; I-Type: cargar 0 en R15")
    print("7. LOOP: CMP R0, R15   ; R-Type: comparar R0 con 0")
    
    # JZ END_FACTORIAL - J-Type
    end_factorial_addr = 8 * 11  # Ajustar direccion
    instructions.append(decoder.encode_j_type(
        Opcodes.JZ, end_factorial_addr, func=0
    ))
    print("8. JZ END_FACTORIAL    ; J-Type: saltar si R0 == 0")
    
    # MUL R1, R1, R0 - R-Type
    instructions.append(decoder.encode_r_type(
        Opcodes.MUL, rd=1, rs1=1, rs2=0, func=0
    ))
    print("9. MUL R1, R1, R0      ; R-Type: R1 = R1 * R0")
    
    # SUB R0, R0, #1  (decrementar contador)
    # Cargar 1 en registro temporal
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=14, rs1=0, imm32=1, func=0  # R14 = 1
    ))
    instructions.append(decoder.encode_r_type(
        Opcodes.SUB, rd=0, rs1=0, rs2=14, func=0  # R0 = R0 - 1
    ))
    print("10. MOV R14, #1        ; I-Type: cargar 1 en R14")
    print("11. SUB R0, R0, R14    ; R-Type: R0 = R0 - 1")
    
    # JMP LOOP - J-Type
    instructions.append(decoder.encode_j_type(
        Opcodes.JMP, loop_addr, func=0
    ))
    print("12. JMP LOOP           ; J-Type: saltar al bucle")
    
    # END_FACTORIAL: RET - S-Type
    instructions.append(decoder.encode_s_type(Opcodes.RET))
    print("13. END_FACTORIAL: RET ; S-Type: retornar")
    
    # Ejecutar
    program = bytearray()
    for inst in instructions:
        program.extend(struct.pack('<Q', inst))
    
    cpu.load_program(bytes(program))
    print("\nEjecutando...")
    cpu.run(max_cycles=100)  # Limitar ciclos
    
    print(f"\nResultados:")
    print(f"Numero original: 4")
    print(f"Factorial (R2): {cpu.registers[2]} (esperado: 24)")
    print(f"Ciclos ejecutados: {cpu.cycle_count}")
    print()


def example_memory_operations():
    """Ejemplo de operaciones con memoria"""
    print("=== EJEMPLO: OPERACIONES CON MEMORIA ===")
    
    cpu = CPU()
    decoder = InstructionDecoder()
    instructions = []
    
    print("Programa: Almacenar y cargar datos de memoria")
    print("Instrucciones:")
    
    # MOV R0, #1000  (direccion base) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=0, rs1=0, imm32=1000, func=0
    ))
    print("1. MOV R0, #1000       ; I-Type: direccion base")
    
    # MOV R1, #42    (valor a almacenar) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=1, rs1=0, imm32=42, func=0
    ))
    print("2. MOV R1, #42         ; I-Type: valor a almacenar")
    
    # STORE [R0], R1   (almacenar R1 en direccion R0) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.STORE, rd=0, rs1=1, imm32=0, func=0  # usar rs1 como fuente
    ))
    print("3. STORE [R0], R1      ; I-Type: almacenar en memoria")
    
    # MOV R2, #0     (limpiar R2) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.MOV, rd=2, rs1=0, imm32=0, func=0
    ))
    print("4. MOV R2, #0          ; I-Type: limpiar R2")
    
    # LOAD R2, [R0]    (cargar desde direccion R0 a R2) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.LOAD, rd=2, rs1=0, imm32=0, func=0  # usar rs1 como direccion
    ))
    print("5. LOAD R2, [R0]       ; I-Type: cargar de memoria")
    
    # HALT - S-Type
    instructions.append(decoder.encode_s_type(Opcodes.HALT))
    print("6. HALT                ; S-Type: detener CPU")
    
    # Ejecutar
    program = bytearray()
    for inst in instructions:
        program.extend(struct.pack('<Q', inst))
    
    cpu.load_program(bytes(program))
    print("\nEjecutando...")
    cpu.run()
    
    print(f"\nResultados:")
    print(f"Direccion (R0): {cpu.registers[0]}")
    print(f"Valor original (R1): {cpu.registers[1]}")
    print(f"Valor cargado (R2): {cpu.registers[2]} (esperado: 42)")
    print(f"Valor en memoria[1000]: {cpu._read_memory_64(1000)}")
    print()


def example_stack_operations():
    """Ejemplo de operaciones con pila"""
    print("=== EJEMPLO: OPERACIONES CON PILA ===")
    
    cpu = CPU()
    decoder = InstructionDecoder()
    instructions = []
    
    print("Programa: Operaciones PUSH y POP")
    print("Instrucciones:")
    
    # PUSH #10 - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.PUSH, rd=0, rs1=0, imm32=10, func=0
    ))
    print("1. PUSH #10            ; I-Type: apilar valor inmediato")
    
    # PUSH #20 - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.PUSH, rd=0, rs1=0, imm32=20, func=0
    ))
    print("2. PUSH #20            ; I-Type: apilar valor inmediato")
    
    # PUSH #30 - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.PUSH, rd=0, rs1=0, imm32=30, func=0
    ))
    print("3. PUSH #30            ; I-Type: apilar valor inmediato")
    
    # POP R0  (debe obtener 30) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.POP, rd=0, rs1=0, imm32=0, func=0
    ))
    print("4. POP R0              ; I-Type: desapilar a R0 (debe ser 30)")
    
    # POP R1  (debe obtener 20) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.POP, rd=1, rs1=0, imm32=0, func=0
    ))
    print("5. POP R1              ; I-Type: desapilar a R1 (debe ser 20)")
    
    # POP R2  (debe obtener 10) - I-Type
    instructions.append(decoder.encode_i_type(
        Opcodes.POP, rd=2, rs1=0, imm32=0, func=0
    ))
    print("6. POP R2              ; I-Type: desapilar a R2 (debe ser 10)")
    
    # HALT - S-Type
    instructions.append(decoder.encode_s_type(Opcodes.HALT))
    print("7. HALT                ; S-Type: detener CPU")
    
    # Ejecutar
    program = bytearray()
    for inst in instructions:
        program.extend(struct.pack('<Q', inst))
    
    cpu.load_program(bytes(program))
    initial_sp = cpu.stack_pointer
    print(f"\nStack Pointer inicial: {initial_sp}")
    
    print("Ejecutando...")
    cpu.run()
    
    print(f"\nResultados (orden LIFO):")
    print(f"R0: {cpu.registers[0]} (esperado: 30)")
    print(f"R1: {cpu.registers[1]} (esperado: 20)")
    print(f"R2: {cpu.registers[2]} (esperado: 10)")
    print(f"Stack Pointer final: {cpu.stack_pointer} (esperado: {initial_sp})")
    print()


def run_all_examples():
    """Ejecuta todos los ejemplos"""
    print("=" * 60)
    print("EJEMPLOS DE USO DE LA CPU EMULADA")
    print("=" * 60)
    print()
    
    examples = [
        example_basic_arithmetic,
        example_logical_operations,
        example_conditional_jumps,
        example_subroutine_call,
        example_memory_operations,
        example_stack_operations
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
            print(f"✓ Ejemplo {i} completado exitosamente")
        except Exception as e:
            print(f"✗ Ejemplo {i} fallo: {e}")
        print("-" * 40)
    
    print("Todos los ejemplos han sido ejecutados.")


if __name__ == "__main__":
    run_all_examples()