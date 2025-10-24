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

    return min_addr, max_addr


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
        min_addr, max_addr = load(memory, bin_path, map_path)
        print(
            f"Cargado en memoria: {min_addr} (0x{min_addr:x}) - {max_addr} (0x{max_addr:x})"
        )

        if ram_display:
            ram_display.update_memory(memory, min_addr, max_addr)
    else:
        print("\033[33m No se pudo enlazar \033[0m")
