import customtkinter as ctk
from .design_variable_elements import Fonts

class ProgramCounterFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.cpu = kwargs.get("cpu", None)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.__build_widgets()

    def __build_widgets(self):
        label = ctk.CTkLabel(
            self, text="PC:", font=Fonts.get_font("consolas"), text_color="white"
        )
        label.grid(row=0, column=0, sticky="e", padx=5)

        self.pc_entry = ctk.CTkEntry(
            self,
            font=Fonts.get_font("consolas"),
            text_color="#00FF00",
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#00FF00",
        )
        self.pc_entry.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.pc_entry.insert(0, "0")

        # Binding para actualizar PC al presionar Enter
        self.pc_entry.bind("<Return>", self.__on_pc_enter)

    def __on_pc_enter(self, event=None):
        """Actualiza el PC del CPU cuando el usuario presiona Enter."""
        if not self.cpu:
            print("CPU no disponible")
            return

        try:
            pc_text = self.pc_entry.get().strip()
            if not pc_text:
                return

            # Aceptar decimal, hex (0x...) o binario (0b...)
            if pc_text.lower().startswith("0x"):
                new_pc = int(pc_text, 16)
            elif pc_text.lower().startswith("0b"):
                new_pc = int(pc_text, 2)
            else:
                # Interpretar como posición de palabra (word_position), convertir a byte address
                word_pos = int(pc_text, 10)
                new_pc = word_pos * 8

            # Validar rango
            if hasattr(self.cpu, "memory") and self.cpu.memory:
                max_addr = self.cpu.memory.size
            else:
                max_addr = 1024 * 1024  # Default 1MB

            if new_pc < 0 or new_pc >= max_addr:
                print(f"PC fuera de rango: {new_pc} (memoria: 0-{max_addr - 1})")
                # Restaurar valor anterior
                self.update_pc(self.cpu.pc)
                return

            # Setear PC
            self.cpu.pc = new_pc

            # Actualizar display
            word_position = new_pc // 8
            self.pc_entry.delete(0, "end")
            self.pc_entry.insert(0, str(word_position))

            print(f"PC actualizado a: {new_pc} (palabra {word_position}, 0x{new_pc:X})")

        except ValueError as e:
            print(f"Valor inválido para PC: {e}")
            # Restaurar valor anterior si hay error
            if self.cpu:
                self.update_pc(self.cpu.pc)

    def update_pc(self, pc: int):
        """Actualiza el valor del Program Counter mostrando posición de palabra"""
        word_position = pc // 8
        self.pc_entry.delete(0, "end")
        self.pc_entry.insert(0, str(word_position))
