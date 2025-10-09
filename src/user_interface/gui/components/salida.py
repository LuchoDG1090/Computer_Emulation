import customtkinter as ctk

class SalidaFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color = '#0c1826', **kwargs):
        super().__init__(parent, fg_color = fg_color)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)

        self.__build_text()
        self.__build_output_frame()
    
    def __build_text(self):
        text = ctk.CTkLabel(
            self,
            text = 'Salida',
            font=("Comic Sans MS", 14),
            text_color="white"
        )
        text.grid(column = 0, row = 0, sticky = 'nsew')

    def __build_output_frame(self):
        output_frame = ctk.CTkTextbox(
            self,
            fg_color = '#2b2b2b'
        )
        output_frame.grid(column = 0, row = 1, sticky = 'nsew', pady = 5)