import customtkinter as ctk
from PIL import Image

from ..func import cpu_control
from .design_variable_elements import Fonts

class CompleteExecute(ctk.CTkFrame):
    def __init__(self, parent, fg_color = 'transparent', **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.cpu = kwargs.get('cpu', None)
        self.update_callback = kwargs.get('update_callback', None)

        self.__makebutton()
        self.__tempo_switch()
        self.__tempo_value()
    
    def __makebutton(self):
        # ejecutar_completo_imagen = ctk.CTkImage(
        #     light_image = Image.open(),
        #     dark_image = Image.open(),
        #     size = (40, 40)
        # )
        self.ejecutar_completo = ctk.CTkButton(
            self, 
            text = 'Ejecutar completo',
            # image = ejecutar_completo_imagen,
            # compound = 'right',
            fg_color="#4C44AC",
            text_color="white",
            corner_radius=50,
            font=Fonts.get_font(""),
            command=self.__complete_execute
        )
        self.ejecutar_completo.grid(column=0, row=0, sticky="nsew", pady = 5)
    

    def __tempo_switch(self):
        self.tempo_ejecutar = ctk.CTkButton(
            self,
            text = "Ejecutar con temporizador",
            fg_color="#4C44AC",
            text_color = "white",
            corner_radius=50,
            font=Fonts.get_font(""),
            command = self.__delay_execute
        )
        self.tempo_ejecutar.grid(column = 1, row = 0, sticky = "nsew", pady = 5)
    

    def __tempo_value(self):
        vcmd = (self.register(self.only_numbers), "%P")
        self.tempo_value = ctk.CTkEntry(
            self,
            placeholder_text = "Delay(s)",
            font = Fonts.get_font(""),
            validate="key",
            validatecommand=vcmd
        )

        self.tempo_value.grid(column = 2, row = 0, sticky = "nsew", pady = 5)
    
    def only_numbers(self, new_value):
        """Permite solo números vacíos o dígitos."""
        return new_value.isdigit() or new_value == ""
    
    def __delay_execute(self):
        value = self.tempo_value.get()

        if value.isdigit():
            delay = int(value)
        else:
            delay = 1

        cpu_control.tempo_execute(self.cpu, delay, self.update_callback)

    def __complete_execute(self):
        cpu_control.complete_execute(self.cpu, self.update_callback)