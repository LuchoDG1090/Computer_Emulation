import customtkinter as ctk


class DinamicRandomAccessMemory(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.memory = kwargs.get("memory", None)

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
        self.memory_textbox.bind("<Return>", self.__on_memory_edit)

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

    def __on_memory_edit(self, event):
        """Aplica cambio cuando se presiona Enter en una línea de memoria"""
        if not self.memory:
            return "break"

        # Obtener la línea actual
        current_pos = self.memory_textbox.index("insert")
        line_num = current_pos.split(".")[0]
        line = self.memory_textbox.get(f"{line_num}.0", f"{line_num}.end").strip()

        # Saltar si es header o separador
        if not line or "Posición" in line or line.startswith("-"):
            return

        parts = line.split()
        if len(parts) >= 2:
            try:
                word_pos = int(parts[0])
                hex_value = parts[1]

                # Remover prefijo 0x si existe
                if hex_value.startswith("0x") or hex_value.startswith("0X"):
                    hex_value = hex_value[2:]

                # Convertir a entero
                value = int(hex_value, 16)

                # Escribir en memoria (convertir posición de palabra a bytes)
                byte_addr = word_pos * 8
                self.memory.write_word(byte_addr, value)

            except ValueError as e:
                print(f"Error al modificar memoria: {line} - {e}")

        return "break"

    def clear_memory(self):
        """Limpia la visualización de la memoria"""
        self.memory_textbox.delete("1.0", "end")
        header = f"{'Posición':<12} {'Contenido (Hex)'}\n"
        header += "-" * 40 + "\n"
        self.memory_textbox.insert("1.0", header)
