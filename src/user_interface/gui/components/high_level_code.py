import customtkinter as ctk
from PIL import Image

class HighLevelCodeFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color = '#0C1826', **kwargs):
        super().__init__(parent, fg_color = fg_color)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)
        self.compile_icon = kwargs.get('compile_icon', '')
        self.upload_icon = kwargs.get('upload_icon', '')

        self.__build_text()
        self.__build_entry_text()
        self.__build_buttons()

    def __build_text(self):
        text = ctk.CTkLabel(
            self,
            text = 'Código en alto nivel',
            font=("Comic Sans MS", 14),
            text_color="white"
        )
        text.grid(row = 0, column = 0)

    def __build_entry_text(self):
        text_entry = ctk.CTkTextbox(
            self,
            fg_color = '#2b2b2b'
        )
        text_entry.grid(row = 1, column = 0, sticky = 'nsew', padx = 12)

    def __build_buttons(self):
        button_frame = ctk.CTkFrame(
            self,
            fg_color = 'transparent'
        )

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.rowconfigure(0, weight=1)

        compile_image = ctk.CTkImage(
            light_image = Image.open(self.compile_icon),
            dark_image = Image.open(self.compile_icon),
            size = (40, 40)
        )
        boton_compilar = ctk.CTkButton(
            button_frame, 
            text='Compilar',
            image = compile_image,
            compound='right',
            fg_color='#4C44AC',
            text_color='white',
            corner_radius=50,
            font=("Comic Sans MS", 16, "bold"),
        )
        boton_compilar.grid(row = 0, column = 0)

        upload_image = ctk.CTkImage(
            light_image = Image.open(self.upload_icon),
            dark_image = Image.open(self.upload_icon),
            size = (40, 40)
        )
        boton_subir = ctk.CTkButton(
            button_frame, 
            text='Subir',
            image = upload_image,
            compound='right',
            fg_color='#4C44AC',
            text_color='white',
            corner_radius=50,
            font=("Comic Sans MS", 16, "bold"),
        )
        boton_subir.grid(row = 0, column = 1)

        button_frame.grid(column = 0, row = 2, sticky = 'nsew', padx = 30)