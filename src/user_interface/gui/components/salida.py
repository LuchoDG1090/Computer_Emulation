import customtkinter as ctk


class SalidaFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.grid_propagate(False)

        self.__build_text()
        self.__build_output_frame()

    def __build_text(self):
        text = ctk.CTkLabel(
            self, text="Salida", font=("Comic Sans MS", 14), text_color="white"
        )
        text.grid(column=0, row=0, sticky="nsew")

    def __build_output_frame(self):
        self.output_textbox = ctk.CTkTextbox(self, fg_color="#2b2b2b")
        self.output_textbox.grid(column=0, row=1, sticky="ew", pady=5, padx=5)

    def append_char(self, char_code: int):
        """Agrega un carácter a la salida"""
        try:
            char = chr(char_code)
        except Exception:
            char = f"[0x{char_code:02X}]"

        self.output_textbox.insert("end", char)
        self.output_textbox.see("end")

    def append_int(self, value: int):
        """Agrega un entero a la salida con newline"""
        self.output_textbox.insert("end", f"{value}\n")
        self.output_textbox.see("end")

    def clear_output(self):
        """Limpia la salida"""
        self.output_textbox.delete("1.0", "end")
