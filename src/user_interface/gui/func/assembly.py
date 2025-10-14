from customtkinter import filedialog
from src.assembler import assembler_new_version as assembler


def select_file():
    ruta = filedialog.askopenfilename(
        title = 'Seleccionar script de codigo ensamblador',
        filetypes=(("Archivos ensamblador", "*.asm"), ("Todos los archivos", "*.*"))
    )
    return ruta

def open_file(ruta):
    with open(ruta, 'r') as f:
        return f.read()

def load_content(textbox) -> None:
    textbox.delete("1.0", "end")
    textbox.insert("1.0", open_file(select_file()))

def clean_content(textbox) -> None:
    textbox.delete("1.0", "end")

def get_textbox_lines(textbox):
    contenido = textbox.get("1.0", "end")
    return contenido.strip().split('\n')

def assemble(textbox_origen, textbox_destino):
    contenido = get_textbox_lines(textbox_origen)
    resolve = assembler.Assembler().assemble(lines = contenido)
    textbox_destino(resolve)

