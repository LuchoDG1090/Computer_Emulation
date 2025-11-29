from tkinter import messagebox
import customtkinter as ctk
from .design_variable_elements import Fonts


class ConsoleFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  
        self.rowconfigure(1, weight=1)  
        self.rowconfigure(2, weight=0)  
        self.rowconfigure(3, weight=1)
        self.grid_propagate(False)

        self.waiting_for_input = False
        self.input_type = None
        self.input_result = None
        self.input_start_pos = None
        self.input_buffer = []

        self.__build_title()
        self.__build_console()

    # -----------------------------------------------------------
    # TITULOS
    # -----------------------------------------------------------
    def __build_title(self):
        text = ctk.CTkLabel(
            self, text="Consola", font=Fonts.get_font("global_mini"), text_color="white"
        )
        text.grid(column=0, row=0, sticky="nsew")

        text2 = ctk.CTkLabel(
            self, text="Entrada de usuario", font=Fonts.get_font("global_mini"), text_color="white"
        )
        text2.grid(column=0, row=2, sticky="nsew")

    # -----------------------------------------------------------
    # CONSTRUCCIÓN DE CONSOLAS
    # -----------------------------------------------------------
    def __build_console(self):
        # Salida (stdout)
        self.console_textbox = ctk.CTkTextbox(self, fg_color="#2b2b2b", wrap="word")
        self.console_textbox.configure(state="disabled")

        # Entrada (stdin)
        self.entrada_textbox = ctk.CTkTextbox(self, fg_color="#2b2b2b", wrap="word")
        self.entrada_textbox.configure(state="disabled")

        self.console_textbox.grid(column=0, row=1, sticky="nsew", pady=5, padx=5)
        self.entrada_textbox.grid(column=0, row=3, sticky="nsew", pady=5, padx=5)

        # Eventos
        self.entrada_textbox.bind("<Return>", self.__on_enter)
        self.entrada_textbox.bind("<Key>", self.__on_key)

    # -----------------------------------------------------------
    # MANEJO DE EDICIÓN EN ENTRADA
    # -----------------------------------------------------------
    def __on_key(self, event):
        if not self.waiting_for_input:
            return "break"

        # Permitir cualquier tecla válida
        if self.input_start_pos:
            current_pos = self.entrada_textbox.index("insert")
            if self.entrada_textbox.compare(current_pos, "<", self.input_start_pos):
                return "break"

        # Evitar borrar antes del inicio
        if event.keysym in ["BackSpace", "Left"]:
            current_pos = self.entrada_textbox.index("insert")
            if self.entrada_textbox.compare(current_pos, "<=", self.input_start_pos):
                return "break"

    # -----------------------------------------------------------
    # PROCESAR ENTER
    # -----------------------------------------------------------
    def __on_enter(self, event):
        if not self.waiting_for_input:
            return "break"

        user_input = self.entrada_textbox.get("1.0", "end-1c").strip()

        # Tipo char
        if self.input_type == "char":
            self.input_result = ord(user_input[0]) if user_input else 0

        # Tipo int
        elif self.input_type == "int":
            try:
                if not user_input:
                    raise ValueError
                parts = [int(x) for x in user_input.split()]
                self.input_result = parts[0]
                if len(parts) > 1:
                    self.input_buffer.extend(parts[1:])
            except ValueError:
                messagebox.showerror("Error", "Debe ingresar números válidos")
                self.entrada_textbox.delete("1.0", "end")
                return "break"

        # Tipo línea
        elif self.input_type == "line":
            self.input_result = user_input

        # Limpiar entrada
        self.entrada_textbox.delete("1.0", "end")
        self.entrada_textbox.configure(state="disabled")

        self.waiting_for_input = False

        return "break"

    # -----------------------------------------------------------
    # MÉTODOS DE SALIDA (stdout)
    # -----------------------------------------------------------

    def append_char(self, char_code: int):
        self.console_textbox.configure(state="normal")
        try:
            char = chr(char_code)
        except Exception:
            char = f"[0x{char_code:02X}]"

        self.console_textbox.insert("end", char)
        self.console_textbox.see("end")
        self.console_textbox.configure(state="disabled")

    def append_int(self, value: int):
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert("end", str(value))
        self.console_textbox.see("end")
        self.console_textbox.configure(state="disabled")

    # -----------------------------------------------------------
    # MÉTODOS DE ENTRADA (stdin)
    # -----------------------------------------------------------
    def request_char(self) -> int:
        self.__activate_stdin("char")
        self.__wait_for_input()
        return self.input_result or 0

    def request_int(self) -> int:
        if self.input_buffer:
            return self.input_buffer.pop(0)

        self.__activate_stdin("int")
        self.__wait_for_input()
        return self.input_result or 0

    def request_line(self) -> str:
        self.__activate_stdin("line")
        self.__wait_for_input()
        return self.input_result or ""

    # -----------------------------------------------------------
    # ACTIVACION REAL DE STDIN
    # -----------------------------------------------------------
    def __activate_stdin(self, t):
        self.input_type = t
        self.input_result = None
        self.waiting_for_input = True

        self.entrada_textbox.configure(state="normal")
        self.entrada_textbox.delete("1.0", "end")
        self.entrada_textbox.focus()

        self.input_start_pos = self.entrada_textbox.index("end-1c")

    # -----------------------------------------------------------
    # ESPERA BLOQUEANTE
    # -----------------------------------------------------------
    def __wait_for_input(self):
        var = ctk.StringVar()

        def check():
            if not self.waiting_for_input:
                var.set("ready")
            else:
                self.after(50, check)

        check()
        self.console_textbox.wait_variable(var)

    # -----------------------------------------------------------
    # UTILIDADES
    # -----------------------------------------------------------
    def clear_console(self):
        self.console_textbox.configure(state="normal")
        self.console_textbox.delete("1.0", "end")
        self.console_textbox.configure(state="disabled")

        self.entrada_textbox.configure(state="disabled")
        self.entrada_textbox.delete("1.0", "end")

        self.waiting_for_input = False
        self.input_result = None
        self.input_start_pos = None
        self.input_buffer = []
