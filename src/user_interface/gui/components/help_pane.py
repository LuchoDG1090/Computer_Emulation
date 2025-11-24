import customtkinter as ctk

class HelpPane(ctk.CTkFrame):
    def __init__(self, parent, height, width, **kwargs):
        super().__init__(parent, width=width, height=height, fg_color="transparent")
        pass