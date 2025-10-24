"""Funciones de control de ejecución del CPU"""

from .compilation_registry import CompilationRegistry


def execute_step(cpu, update_callback=None):
    """
    Ejecuta una instrucción del CPU y actualiza la interfaz

    Args:
        cpu: Instancia del CPU
        update_callback: Función para actualizar la GUI con el estado del CPU
    """
    if not cpu.running:
        cpu.running = True

    try:
        should_continue = cpu.step()

        if update_callback:
            update_callback(cpu.get_state())

        if not should_continue:
            cpu.running = False
            print("Programa terminado")

        return should_continue

    except Exception as e:
        cpu.running = False
        print(f"Error en ejecución: {e}")
        return False


def reset_cpu(
    cpu,
    update_callback=None,
    clear_output_callback=None,
    clear_ram_callback=None,
    clear_programs_callback=None,
):
    """
    Reinicia el CPU al estado inicial

    Args:
        cpu: Instancia del CPU
        update_callback: Función para actualizar la GUI con el estado del CPU
        clear_output_callback: Función para limpiar la salida
        clear_ram_callback: Función para limpiar la visualización de RAM
        clear_programs_callback: Función para limpiar los programas cargados
    """
    cpu.reset()

    # Limpiar programas cargados
    CompilationRegistry.clear_loaded_programs()

    if clear_output_callback:
        clear_output_callback()

    if clear_ram_callback:
        clear_ram_callback()

    if clear_programs_callback:
        clear_programs_callback()

    if update_callback:
        update_callback(cpu.get_state())

    print("CPU reiniciado")
