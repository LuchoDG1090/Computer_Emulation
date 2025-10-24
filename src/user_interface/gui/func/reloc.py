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


def load(memory, bin_path, map_path):
    from src.memory.linker import Linker

    program_words, map_entries = Linker.analizar_programa(bin_path, map_path)
    min_addr, max_addr = loader.Loader.cargar_bin(memory, program_words, map_entries)

    # Obtener punto de entrada (primera dirección ejecutable)
    entry_point = None
    for entry in map_entries:
        if entry.flag == 1:
            if entry_point is None or entry.address < entry_point:
                entry_point = entry.address

    return min_addr, max_addr, entry_point


def link_load(textbox, memory, ram_display=None):
    contenido = textbox.get("1.0", "end").strip()

    entry = CompilationRegistry.find_by_content(contenido)

    if not entry:
        print("\033[33m El código no coincide con ningún programa compilado \033[0m")
        return

    bin_path = entry["bin_path"]
    map_path = entry["map_path"]

    if link(bin_path, map_path):
        print("Enlazado correctamente")
        min_addr, max_addr, entry_point = load(memory, bin_path, map_path)

        # Determinar nombre del programa
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

        print(
            f"Programa '{program_name}' cargado en memoria: {min_addr} (0x{min_addr:x}) - {max_addr} (0x{max_addr:x})"
        )
        print(f"Punto de entrada: {entry_point} (0x{entry_point:x})")

        if ram_display:
            ram_display.update_memory(memory, min_addr, max_addr)
    else:
        print("\033[33m No se pudo enlazar \033[0m")
