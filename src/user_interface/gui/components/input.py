from tkinter import simpledialog

import customtkinter as ctk


class userInputBox(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0C1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.__build_title()
        self.__build_text_box_area()

    def __build_title(self):
        title = ctk.CTkLabel(self, text="Input", font=("Comic Sans MS", 14, "bold"))
        title.grid(column=0, row=0, sticky="nsew")

    def __build_text_box_area(self):
        self.entry = ctk.CTkEntry(self)
        self.entry.grid(column=0, row=1, sticky="nsew")

    def request_char(self) -> int:
        """Solicita un carácter del usuario"""
        result = simpledialog.askstring("Entrada", "Ingrese un carácter:")
        if result and len(result) > 0:
            return ord(result[0])
        return 0

    def request_int(self) -> int:
        """Solicita un entero del usuario"""
        result = simpledialog.askinteger("Entrada", "Ingrese un número:")
        if result is not None:
            return result
        return 0
