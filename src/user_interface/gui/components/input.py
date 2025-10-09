import customtkinter as ctk

class userInputBox(ctk.CTkFrame):
    def __init__(self, parent, fg_color = '#0C1826', **kwargs):
        super().__init__(parent, fg_color = fg_color)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)

        self.__build_title()
        self.__build_text_box_area()

    def __build_title(self):
        title = ctk.CTkLabel(
            self,
            text = 'Input',
            font=("Comic Sans MS", 14, "bold")
        )
        title.grid(column = 0, row = 0, sticky = 'nsew')

    def __build_text_box_area(self):
        entry = ctk.CTkEntry(
            self
        )
        entry.grid(column = 0, row = 1, sticky = 'nsew')