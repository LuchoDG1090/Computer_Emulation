"""Funciones de control de ejecución del CPU"""


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


def reset_cpu(cpu, update_callback=None):
    """
    Reinicia el CPU al estado inicial

    Args:
        cpu: Instancia del CPU
        update_callback: Función para actualizar la GUI con el estado del CPU
    """
    cpu.reset()

    if update_callback:
        update_callback(cpu.get_state())

    print("CPU reiniciado")
