#!/usr/bin/env python3
"""
Script principal para ejecutar ejemplos del emulador de CPU

Este script permite ejecutar diferentes ejemplos y demostraciones
del emulador de CPU
"""

import sys
import os

# Añadir directorios al path
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, 'src'))
sys.path.append(os.path.join(current_dir, 'examples'))

from cpu.cpu import CPU, InstructionDecoder, Opcodes, InstructionType

# Importar funciones especificas
def import_examples():
    """Importa las funciones de ejemplo de forma segura"""
    try:
        import cpu_examples
        return {
            'example_basic_arithmetic': cpu_examples.example_basic_arithmetic,
            'example_logical_operations': cpu_examples.example_logical_operations,
            'example_conditional_jumps': cpu_examples.example_conditional_jumps,
            'example_subroutine_call': cpu_examples.example_subroutine_call,
            'example_memory_operations': cpu_examples.example_memory_operations,
            'example_stack_operations': cpu_examples.example_stack_operations,
            'run_all_examples': cpu_examples.run_all_examples
        }
    except ImportError as e:
        print(f"Error importando ejemplos: {e}")
        return {}

def print_menu():
    """Muestra el menu de opciones disponibles"""
    print("\n" + "="*60)
    print("    EMULADOR DE CPU EUCLID-64 - MENU PRINCIPAL")
    print("="*60)
    print("1. Operaciones Aritmeticas Basicas")
    print("2. Operaciones Logicas")
    print("3. Saltos Condicionales")
    print("4. Llamadas a Subrutinas") 
    print("5. Operaciones de Memoria")
    print("6. Operaciones de Pila")
    print("7. Ejecutar Todos los Ejemplos")
    print("8. Crear CPU Personalizado")
    print("9. Mostrar Informacion del Formato")
    print("0. Salir")
    print("-"*60)

def run_example(choice):
    """Ejecuta el ejemplo seleccionado"""
    example_funcs = import_examples()
    examples = {
        1: ("Operaciones Aritmeticas Basicas", example_funcs.get('example_basic_arithmetic')),
        2: ("Operaciones Logicas", example_funcs.get('example_logical_operations')),
        3: ("Saltos Condicionales", example_funcs.get('example_conditional_jumps')),
        4: ("Llamadas a Subrutinas", example_funcs.get('example_subroutine_call')),
        5: ("Operaciones de Memoria", example_funcs.get('example_memory_operations')),
        6: ("Operaciones de Pila", example_funcs.get('example_stack_operations'))
    }
    
    if choice in examples:
        name, func = examples[choice]
        if func is None:
            print(f"Funcion de ejemplo no encontrada para: {name}")
            return
        print(f"\nEjecutando: {name}")
        print("-" * 40)
        try:
            func()
            print(f"- {name} completado exitosamente")
        except Exception as e:
            print(f"Error en {name}: {e}")
    else:
        print("Opcion no valida")

def run_all_examples():
    """Ejecuta todos los ejemplos disponibles"""
    print("\nEjecutando todos los ejemplos de instrucciones...")
    example_funcs = import_examples()
    
    # Usar la funcion run_all_examples del modulo cpu_examples si esta disponible
    if 'run_all_examples' in example_funcs and example_funcs['run_all_examples'] is not None:
        try:
            example_funcs['run_all_examples']()
            return
        except Exception as e:
            print(f"Error ejecutando run_all_examples: {e}")
    
    # Fallback: ejecutar ejemplos individualmente
    examples = [
        ("Operaciones Aritmeticas Basicas", example_funcs.get('example_basic_arithmetic')),
        ("Operaciones Logicas", example_funcs.get('example_logical_operations')), 
        ("Saltos Condicionales", example_funcs.get('example_conditional_jumps')),
        ("Llamadas a Subrutinas", example_funcs.get('example_subroutine_call')),
        ("Operaciones de Memoria", example_funcs.get('example_memory_operations')),
        ("Operaciones de Pila", example_funcs.get('example_stack_operations'))
    ]
    
    for name, func in examples:
        if func is None:
            print(f"{name} - FUNCIoN NO ENCONTRADA")
            continue
            
        print(f"\n{'='*50}")
        print(f"Ejecutando: {name}")
        print('='*50)
        try:
            func()
            print(f"- {name} - EXITOSO")
        except Exception as e:
            print(f"- {name} - ERROR: {e}")
    
    print(f"\n{'='*50}")
    print("Todos los ejemplos completados")
    print('='*50)

def create_custom_cpu():
    """Permite crear y configurar un CPU personalizado"""
    print("\nCreando CPU Personalizado")
    print("-" * 40)
    
    try:
        # Solicitar tamaño de memoria
        memory_size = input("Tamaño de memoria (bytes, default 65536): ").strip()
        if not memory_size:
            memory_size = 65536
        else:
            memory_size = int(memory_size)
        
        # Crear CPU y decodificador
        cpu = CPU(memory_size=memory_size)
        decoder = InstructionDecoder()
        print(f"CPU creado con {memory_size} bytes de memoria")
        
        # Mostrar estado inicial
        print("\nEstado inicial del CPU:")
        print(f"PC: 0x{cpu.pc:016X}")
        print(f"Accumulator: 0x{cpu.accumulator:016X}")
        print(f"Flags: {cpu.flags:08b}")
        print(f"Stack Pointer: 0x{cpu.stack_pointer:016X}")
        print(f"Memoria disponible: {len(cpu.memory)} bytes")
        print(f"Registros R0-R15: todos en 0x0000000000000000")
        
        # Opcion de cargar programa simple
        load_program = input("\n¿Cargar programa de ejemplo? (y/n): ").strip().lower()
        if load_program == 'y':
            print("\nPrograma de ejemplo: 15 + 25 = 40")
            print("Instrucciones a ejecutar:")
            print("1. MOV R0, #15    ; I-Type: cargar 15 en R0")
            print("2. MOV R1, #25    ; I-Type: cargar 25 en R1") 
            print("3. ADD R2, R0, R1 ; R-Type: R2 = R0 + R1")
            print("4. HALT           ; S-Type: detener CPU")
            
            # Crear programa usando formato
            instructions = []
            
            # MOV R0, #15
            instructions.append(decoder.encode_i_type(
                Opcodes.MOV, rd=0, rs1=0, imm32=15, func=0
            ))
            
            # MOV R1, #25  
            instructions.append(decoder.encode_i_type(
                Opcodes.MOV, rd=1, rs1=0, imm32=25, func=0
            ))
            
            # ADD R2, R0, R1
            instructions.append(decoder.encode_r_type(
                Opcodes.ADD, rd=2, rs1=0, rs2=1, func=0
            ))
            
            # HALT
            instructions.append(decoder.encode_s_type(Opcodes.HALT))
            
            # Convertir a bytes y cargar
            import struct
            program = bytearray()
            for inst in instructions:
                program.extend(struct.pack('<Q', inst))
            
            cpu.load_program(bytes(program))
            print("Programa cargado exitosamente")
            
            # Ejecutar programa
            execute = input("¿Ejecutar programa? (y/n): ").strip().lower()
            if execute == 'y':
                print("\n🏃 Ejecutando programa...")
                try:
                    cpu.run()
                    print(f"Programa completado")
                    print(f"Resultado en R2: {cpu.registers[2]} (esperado: 40)")
                    print(f"R0: {cpu.registers[0]}, R1: {cpu.registers[1]}")
                    print(f"Ciclos ejecutados: {cpu.cycle_count}")
                except Exception as e:
                    print(f"Error durante ejecucion: {e}")
        
    except ValueError:
        print("Error: Tamaño de memoria debe ser un numero")
    except Exception as e:
        print(f"Error creando CPU: {e}")

def show_format_info():
    """Muestra informacion sobre el formato de instrucciones"""
    print("\n" + "="*60)
    print("INFORMACION DEL FORMATO DE INSTRUCCIONES")
    print("="*60)
    
    print("[63-56] Opcode (8 bits)\n[55-52] RD - Registro destino (4 bits)\n[51-48] RS1 - Registro fuente 1 (4 bits)\n[47-44] RS2 - Registro fuente 2 (4 bits)\n[43-32] FUNC - Campo de funcion o modificador (12 bits)\n[31-0]  IMM32 - Campo inmediato/direccion (32 bits)")
    
    input("\nPresione Enter para continuar...")

def main():
    """Funcion principal del script"""
    print("Bienvenido al Emulador de CPU EUCLID-64")
    print("Modulo M1 - Arquitectura Von Neumann")
    
    while True:
        try:
            print_menu()
            choice = input("Seleccione una opcion: ").strip()
            
            if choice == '0':
                print("¡Gracias por usar el emulador de CPU EUCLID-64!")
                break
            elif choice == '7':
                run_all_examples()
            elif choice == '8':
                create_custom_cpu()
            elif choice == '9':
                show_format_info()
            else:
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= 6:
                        run_example(choice_num)
                    else:
                        print("Por favor seleccione una opcion valida (0-9)")
                except ValueError:
                    print("Por favor ingrese un numero valido")
        
        except KeyboardInterrupt:
            print("\n\nPrograma interrumpido por el usuario")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()