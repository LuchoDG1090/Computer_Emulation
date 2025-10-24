import os

from src.memory import linker, loader

from .compilation_registry import CompilationRegistry


def link(bin_path, map_path):
    try:
        linker.Linker.verificar_programa(bin_path, map_path)
        return True
    except Exception as e:
        print(f"Error en verificación: {e}")
        return False


def load(memory, bin_path, map_path, base_address=None):
    """
    Carga un programa en memoria

    Args:
        memory: Objeto Memory
        bin_path: Ruta al archivo .bin
        map_path: Ruta al archivo .map
        base_address: Dirección base para sumar a todas las direcciones (en bytes)
    """
    from src.memory.linker import Linker

    program_words, map_entries = Linker.analizar_programa(bin_path, map_path)
    min_addr, max_addr = loader.Loader.cargar_bin(
        memory, program_words, map_entries, base_address
    )

    # Si se especifica base_address, se suma a todas las direcciones
    offset = base_address if base_address is not None else 0

    # Obtener punto de entrada (primera dirección ejecutable)
    entry_point = None
    for entry in map_entries:
        if entry.flag == 1:
            adjusted_addr = entry.address + offset
            if entry_point is None or adjusted_addr < entry_point:
                entry_point = adjusted_addr

    return min_addr, max_addr, entry_point


def link_load(
    textbox, memory, ram_display=None, base_address=None, program_name_override=None
):
    """
    Enlaza y carga un programa en memoria

    Args:
        textbox: CTkTextbox con el contenido del código relocalizable
        memory: Objeto Memory
        ram_display: Componente para actualizar visualización de RAM
        base_address: Dirección base opcional para reubicación (en bytes)
    """
    contenido = textbox.get("1.0", "end").strip()

    entry = CompilationRegistry.find_by_content(contenido)

    if not entry:
        print("\033[33m El código no coincide con ningún programa compilado \033[0m")
        return

    bin_path = entry["bin_path"]
    map_path = entry["map_path"]

    if link(bin_path, map_path):
        print("Enlazado correctamente")
        min_addr, max_addr, entry_point = load(memory, bin_path, map_path, base_address)

        # Verificar colisión con programas ya cargados
        collision, collision_program = CompilationRegistry.check_collision(
            min_addr, max_addr
        )
        if collision:
            print(
                f"\033[31m Error: El programa colisiona con '{collision_program}' ya cargado en memoria \033[0m"
            )
            # Deshacer la carga escribiendo ceros
            for addr in range(min_addr, max_addr + 1, 8):
                memory.write_word(addr, 0)
            return

        # Determinar nombre del programa (permitir override del usuario)
        if program_name_override:
            program_name = program_name_override
        else:
            program_name = None
            if entry.get("source_filename"):
                # Usar nombre del archivo fuente sin extensión
                program_name = os.path.splitext(entry["source_filename"])[0]
            else:
                # Usar nombre del binario como fallback
                program_name = os.path.splitext(os.path.basename(bin_path))[0]

        # Registrar programa cargado
        CompilationRegistry.register_loaded_program(
            program_name, min_addr, max_addr, entry_point, bin_path, map_path
        )

        # Convertir direcciones de bytes a posiciones de palabra para mostrar
        min_word = min_addr // 8
        max_word = max_addr // 8
        entry_word = entry_point // 8

        print(f"Programa '{program_name}' cargado en memoria: {min_word} - {max_word}")
        print(f"Punto de entrada: {entry_word}")

        if ram_display:
            ram_display.update_memory(memory, min_addr, max_addr)
    else:
        print("\033[33m No se pudo enlazar \033[0m")
