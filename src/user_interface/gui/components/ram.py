import customtkinter as ctk

class DinamicRandomAccessMemory(ctk.CTkFrame):
    def __init__(self, parent, fg_color = '#0c1826', **kwargs):
        super().__init__(parent, fg_color = fg_color)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.__load_title_text()
        self.__load_text_area_ram()
    
    def __load_title_text(self):
        title = ctk.CTkLabel(
            self,
            text = 'Memoria principal - DRAM',
            font = ('Comic Sans MS', 14),
            text_color = 'white'
        )
        title.grid(column = 0, row = 0)

    def __load_text_area_ram(self):
        text_entry = ctk.CTkTextbox(
            self,
            fg_color = '#2b2b2b'
        )
        text_entry.grid(column = 0, row = 1, sticky = 'nsew', padx = 12, pady = 5)