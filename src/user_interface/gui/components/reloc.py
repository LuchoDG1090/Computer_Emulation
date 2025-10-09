import customtkinter as ctk
from PIL import Image

class RelocCodeFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color = '#0C1826', **kwargs):
        super().__init__(parent, fg_color = fg_color)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)
        self.reloc_icon = kwargs.get('reloc_icon', '')

        self.__build_text()
        self.__build_entry_text()
        self.__build_buttons()

    def __build_text(self):
        text = ctk.CTkLabel(
            self,
            text = 'Código relocalizable',
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
        button_frame.rowconfigure(0, weight=1)

        compile_image = ctk.CTkImage(
            light_image = Image.open(self.reloc_icon),
            dark_image = Image.open(self.reloc_icon),
            size = (40, 40)
        )
        boton_compilar = ctk.CTkButton(
            button_frame, 
            text='Enlazar- cargar',
            image = compile_image,
            compound='right',
            fg_color='#4C44AC',
            text_color='white',
            corner_radius=50,
            font=("Comic Sans MS", 16, "bold"),
        )
        boton_compilar.grid(row = 0, column = 0)


        button_frame.grid(column = 0, row = 2, sticky = 'nsew', padx = 30)