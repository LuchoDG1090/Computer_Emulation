from tkinter import messagebox

import customtkinter as ctk


class ConsoleFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.grid_propagate(False)

        self.waiting_for_input = False
        self.input_type = None
        self.input_result = None
        self.input_start_pos = None

        self.__build_title()
        self.__build_console()

    def __build_title(self):
        text = ctk.CTkLabel(
            self, text="Consola", font=("Comic Sans MS", 14), text_color="white"
        )
        text.grid(column=0, row=0, sticky="nsew")

    def __build_console(self):
        self.console_textbox = ctk.CTkTextbox(self, fg_color="#2b2b2b", wrap="word")
        self.console_textbox.grid(column=0, row=1, sticky="nsew", pady=5, padx=5)

        # Bind para manejar entrada del usuario
        self.console_textbox.bind("<Return>", self.__on_enter)
        self.console_textbox.bind("<Key>", self.__on_key)

    def __on_key(self, event):
        """Prevenir edición del texto del programa"""
        if not self.waiting_for_input:
            return "break"

        # Permitir solo edición después de la marca de inicio
        if self.input_start_pos:
            current_pos = self.console_textbox.index("insert")
            if self.console_textbox.compare(current_pos, "<", self.input_start_pos):
                return "break"

        # Bloquear teclas de navegación que moverían el cursor antes del inicio
        if event.keysym in ["BackSpace", "Left"]:
            current_pos = self.console_textbox.index("insert")
            if self.console_textbox.compare(current_pos, "<=", self.input_start_pos):
                return "break"

    def __on_enter(self, event):
        """Manejar entrada del usuario al presionar Enter"""
        if not self.waiting_for_input:
            return "break"

        # Obtener texto desde la posición de inicio
        user_input = self.console_textbox.get(self.input_start_pos, "end-1c")

        # Procesar según el tipo de entrada
        if self.input_type == "char":
            if user_input:
                self.input_result = ord(user_input[0])
            else:
                self.input_result = 0
        elif self.input_type == "int":
            try:
                self.input_result = int(user_input.strip())
            except ValueError:
                messagebox.showerror("Error", "Debe ingresar un número válido")
                self.console_textbox.delete(self.input_start_pos, "end")
                return "break"

        # Agregar newline
        self.console_textbox.insert("end", "\n")
        self.console_textbox.see("end")

        # Marcar como no esperando entrada
        self.waiting_for_input = False
        self.input_start_pos = None

        return "break"

    def append_char(self, char_code: int):
        """Agrega un carácter a la consola"""
        try:
            char = chr(char_code)
        except Exception:
            char = f"[0x{char_code:02X}]"

        self.console_textbox.insert("end", char)
        self.console_textbox.see("end")

    def append_int(self, value: int):
        """Agrega un entero a la consola con newline"""
        self.console_textbox.insert("end", f"{value}\n")
        self.console_textbox.see("end")

    def request_char(self) -> int:
        """Solicita un carácter del usuario"""
        self.input_type = "char"
        self.input_result = None
        self.waiting_for_input = True

        # Marcar posición de inicio de entrada
        self.input_start_pos = self.console_textbox.index("end-1c")

        # Poner foco en la consola
        self.console_textbox.focus()

        # Esperar entrada del usuario
        self.console_textbox.wait_variable(self.__create_wait_var())

        result = self.input_result if self.input_result is not None else 0
        self.input_result = None
        return result

    def request_int(self) -> int:
        """Solicita un entero del usuario"""
        self.input_type = "int"
        self.input_result = None
        self.waiting_for_input = True

        # Marcar posición de inicio de entrada
        self.input_start_pos = self.console_textbox.index("end-1c")

        # Poner foco en la consola
        self.console_textbox.focus()

        # Esperar entrada del usuario
        self.console_textbox.wait_variable(self.__create_wait_var())

        result = self.input_result if self.input_result is not None else 0
        self.input_result = None
        return result

    def __create_wait_var(self):
        """Crea una variable para esperar entrada"""
        var = ctk.StringVar()

        def check_input():
            if not self.waiting_for_input:
                var.set("ready")
            else:
                self.after(50, check_input)

        check_input()
        return var

    def clear_console(self):
        """Limpia la consola"""
        self.console_textbox.delete("1.0", "end")
        self.waiting_for_input = False
        self.input_result = None
        self.input_start_pos = None
