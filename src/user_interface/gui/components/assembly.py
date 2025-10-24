import customtkinter as ctk
from PIL import Image

from src.user_interface.gui.func import assembly as func


class AssemblyCodeFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0C1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.upload_icon = kwargs.get("upload_icon", "")
        self.assemble_icon = kwargs.get("assemble_icon", "")
        self.clean_icon = kwargs.get("clean_icon", "")
        self.funcion_set_reloc = kwargs.get("funcion_set", "")
        self.loaded_file_path = None  # Guardar ruta del archivo cargado

        self.__build_text()
        self.__build_entry_text()
        self.__build_buttons()

    def __build_text(self):
        text = ctk.CTkLabel(
            self, text="Código assembly", font=("Comic Sans MS", 14), text_color="white"
        )
        text.grid(row=0, column=0)

    def __build_entry_text(self):
        self.text_entry = ctk.CTkTextbox(self, fg_color="#2b2b2b")
        self.text_entry.grid(row=1, column=0, sticky="nsew", padx=12)

    def __build_buttons(self):
        button_frame = ctk.CTkFrame(self, fg_color="transparent")

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.rowconfigure(0, weight=1)

        assemble_image = ctk.CTkImage(
            light_image=Image.open(self.assemble_icon),
            dark_image=Image.open(self.assemble_icon),
            size=(40, 40),
        )
        boton_ensamblar = ctk.CTkButton(
            button_frame,
            text="Ensamblar",
            image=assemble_image,
            compound="right",
            fg_color="#4C44AC",
            text_color="white",
            corner_radius=50,
            font=("Comic Sans MS", 16, "bold"),
            command=lambda: func.assemble(
                self.text_entry, self.funcion_set_reloc, self.loaded_file_path
            ),
        )
        boton_ensamblar.grid(row=0, column=0)

        upload_image = ctk.CTkImage(
            light_image=Image.open(self.upload_icon),
            dark_image=Image.open(self.upload_icon),
            size=(40, 40),
        )
        boton_subir = ctk.CTkButton(
            button_frame,
            text="Subir",
            image=upload_image,
            compound="right",
            fg_color="#4C44AC",
            text_color="white",
            corner_radius=50,
            font=("Comic Sans MS", 16, "bold"),
            command=lambda: self.__load_file(),
        )
        boton_subir.grid(row=0, column=1)

        clean_image = ctk.CTkImage(
            light_image=Image.open(self.clean_icon),
            dark_image=Image.open(self.clean_icon),
            size=(40, 40),
        )
        boton_limpiar = ctk.CTkButton(
            button_frame,
            text="Limpiar",
            image=clean_image,
            compound="right",
            fg_color="#4C44AC",
            text_color="white",
            corner_radius=50,
            font=("Comic Sans MS", 16, "bold"),
            command=lambda: func.clean_content(self.text_entry),
        )
        boton_limpiar.grid(row=0, column=2)

        button_frame.grid(column=0, row=2, sticky="nsew", padx=30)

    def __load_file(self):
        """Carga un archivo y guarda su ruta"""
        file_path = func.select_file()
        if file_path:
            self.loaded_file_path = file_path
            content = func.open_file(file_path)
            self.text_entry.delete("1.0", "end")
            self.text_entry.insert("1.0", content)
