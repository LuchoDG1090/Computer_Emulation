from customtkinter import filedialog

def select_file():
    ruta = filedialog.askopenfilename(
        title = 'Seleccionar script de alto nivel',
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
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