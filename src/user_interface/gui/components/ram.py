import customtkinter as ctk


class DinamicRandomAccessMemory(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.__load_title_text()
        self.__load_memory_table()

    def __load_title_text(self):
        title = ctk.CTkLabel(
            self,
            text="Memoria principal - DRAM",
            font=("Comic Sans MS", 14),
            text_color="white",
        )
        title.grid(column=0, row=0)

    def __load_memory_table(self):
        self.memory_textbox = ctk.CTkTextbox(
            self, fg_color="#2b2b2b", font=("Consolas", 14)
        )
        self.memory_textbox.grid(column=0, row=1, sticky="nsew", padx=12, pady=5)

    def update_memory(self, memory, min_addr, max_addr):
        self.memory_textbox.delete("1.0", "end")

        # Header
        header = f"{'Posición':<12} {'Contenido (Hex)'}\n"
        header += "-" * 40 + "\n"

        lines = [header]

        # Convertir rango de bytes a posiciones de palabra
        start_word = min_addr // 8
        end_word = max_addr // 8

        word_pos = start_word
        while word_pos <= end_word:
            addr = word_pos * 8
            value = memory.read_word(addr)
            lines.append(f"{word_pos:<12} 0x{value:016X}\n")
            word_pos += 1

        self.memory_textbox.insert("1.0", "".join(lines))

    def clear_memory(self):
        """Limpia la visualización de la memoria"""
        self.memory_textbox.delete("1.0", "end")
        header = f"{'Posición':<12} {'Contenido (Hex)'}\n"
        header += "-" * 40 + "\n"
        self.memory_textbox.insert("1.0", header)
