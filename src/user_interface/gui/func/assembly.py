from customtkinter import filedialog

from src.assembler import assembler as assembler
from src.assembler.preprocessor import convert_org_word_positions_to_bytes

from .compilation_registry import CompilationRegistry


def select_file():
    ruta = filedialog.askopenfilename(
        title="Seleccionar script de codigo ensamblador",
        filetypes=(("Archivos ensamblador", "*.asm"), ("Todos los archivos", "*.*")),
    )
    return ruta


def open_file(ruta):
    with open(ruta, "r") as f:
        return f.read()


def load_content(textbox) -> None:
    textbox.delete("1.0", "end")
    textbox.insert("1.0", open_file(select_file()))


def clean_content(textbox) -> None:
    textbox.delete("1.0", "end")


def get_textbox_lines(textbox):
    contenido = textbox.get("1.0", "end")
    return contenido.strip().split("\n")


def assemble(textbox_origen, textbox_destino):
    import os
    import tempfile

    contenido = textbox_origen.get("1.0", "end").strip()
    contenido = convert_org_word_positions_to_bytes(contenido)
    asm = assembler.Assembler()
    binary_output = asm.assemble(contenido)

    temp_dir = tempfile.gettempdir()
    bin_path = os.path.join(temp_dir, "program.bin")
    map_path = os.path.join(temp_dir, "program.map")

    with open(bin_path, "w") as f:
        f.write(binary_output)

    with open(map_path, "w") as f:
        for index in asm.memory_map.order:
            entry = asm.memory_map.entries[index]
            f.write(f"{index},0x{entry['address']:08X},{entry['flag']}\n")

    CompilationRegistry.register(binary_output, bin_path, map_path)

    textbox_destino(binary_output)
