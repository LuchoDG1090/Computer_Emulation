import customtkinter as ctk
from PIL import Image

class BotonesAcciones(ctk.CTkFrame):
    def __init__(self, parent, fg_color = 'transparent', **kwargs):
        super().__init__(parent, fg_color = fg_color)
        
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.imagen_siguiente = kwargs.get('imagen_siguiente', '')
        self.imagen_reiniciar = kwargs.get('reiniciar_imagen', '')

        self.__boton_siguiente_instruccion()
        self.__boton_reiniciar()
    
    def __boton_siguiente_instruccion(self):
        siguiente_image = ctk.CTkImage(
            light_image = Image.open(self.imagen_siguiente),
            dark_image = Image.open(self.imagen_siguiente),
            size = (40, 40)
        )
        boton_siguiente = ctk.CTkButton(
            self,
            text = 'Siguiente instruccion',
            image = siguiente_image,
            compound = 'right',
            fg_color='#4C44AC',
            text_color='white',
            corner_radius=50,
            font=("Comic Sans MS", 16, "bold")
        )
        boton_siguiente.grid(column = 0, row = 0, sticky = 'nsew')

    def __boton_reiniciar(self):
        reiniciar_imagen = ctk.CTkImage(
            light_image = Image.open(self.imagen_reiniciar),
            dark_image = Image.open(self.imagen_reiniciar),
            size = (40, 40)
        )
        boton_reiniciar = ctk.CTkButton(
            self,
            text = 'Reiniciar', 
            image = reiniciar_imagen,
            compound = 'right',
            fg_color = '#4C44AC',
            text_color = 'white',
            corner_radius = 50,
            font=("Comic Sans MS", 16, "bold")
        )
        boton_reiniciar.grid(column = 0, row = 1, sticky = 'nsew')