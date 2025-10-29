import customtkinter as ctk
from PIL import Image

from ..func import cpu_control

class CompleteExecute(ctk.CTkFrame):
    def __init__(self, parent, fg_color = 'transparent', **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.cpu = kwargs.get('cpu', None)
        self.update_callback = kwargs.get('update_callback', None)

        self.__makebutton()
    
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
            font=("Comic Sans MS", 16, "bold"),
            command=self.__complete_execute
        )
        self.ejecutar_completo.grid(column=0, row=0, sticky="nsew", pady = 5)


    def __complete_execute(self):
        cpu_control.complete_execute(self.cpu, self.update_callback)