import customtkinter as ctk


class ProgramCounterFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826"):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.__build_widgets()

    def __build_widgets(self):
        label = ctk.CTkLabel(
            self, text="PC:", font=("Consolas", 14, "bold"), text_color="white"
        )
        label.grid(row=0, column=0, sticky="e", padx=5)

        self.pc_value = ctk.CTkLabel(
            self,
            text="0",
            font=("Consolas", 14),
            text_color="#00FF00",
            fg_color="#1a1a1a",
            corner_radius=4,
        )
        self.pc_value.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    def update_pc(self, pc: int):
        """Actualiza el valor del Program Counter mostrando posición de palabra"""
        word_position = pc // 8
        self.pc_value.configure(text=str(word_position))
