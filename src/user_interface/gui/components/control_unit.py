import customtkinter as ctk

class ControlUnitFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color = '#0c1826', **kwargs):
        super().__init__(parent, fg_color = fg_color)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 0)
        self.rowconfigure(1, weight = 1)

        self.__build_text()
        self.__build_table_control_unit()
    
    def __build_text(self):
        control_unit_tiltle = ctk.CTkLabel(
            self,
            text = 'Unidad de control', 
            text_color = 'white',
            font=("Comic Sans MS", 14)
        )
        control_unit_tiltle.grid(column = 0, row = 0)

    def __build_table_control_unit(self):
        scrollable_frame_cu = ctk.CTkScrollableFrame(
            self
        )
        scrollable_frame_cu.grid(column = 0, row = 1, sticky = 'nsew', padx = 5, pady = 5)
        headers = ['registro', 'valor']
        for j, header in enumerate(headers):
            lbl = ctk.CTkLabel(scrollable_frame_cu, text = header, fg_color="#2b2b2b", corner_radius=4)
            lbl.grid(row = 0, column = j, sticky = 'nsew', padx = 5, pady = 5)