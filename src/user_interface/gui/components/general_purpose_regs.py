import customtkinter as ctk


class GeneralPurposeRegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0C1826"):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.register_labels = {}

        self.__build_text()
        self.__build_table()

    def __build_text(self):
        text = ctk.CTkLabel(
            self,
            text="Registros de propósito general",
            font=("Comic Sans MS", 14),
            text_color="white",
        )
        text.grid(row=0, column=0)

    def __build_table(self):
        scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 10), pady=5)

        headers = ["Reg", "Value (Hex)", "Value (Dec)"]
        for j, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                scrollable_frame,
                text=header,
                fg_color="#2b2b2b",
                corner_radius=4,
                font=("Consolas", 11, "bold"),
            )
            lbl.grid(row=0, column=j, sticky="ew", padx=5, pady=5)

        # Crear etiquetas para los 16 registros
        for i in range(16):
            reg_name = f"R{i}"

            name_lbl = ctk.CTkLabel(
                scrollable_frame,
                text=reg_name,
                fg_color="#2b2b2b",
                corner_radius=4,
                font=("Consolas", 10),
            )
            name_lbl.grid(row=i + 1, column=0, sticky="ew", padx=5, pady=2)

            hex_lbl = ctk.CTkLabel(
                scrollable_frame,
                text="0x0000000000000000",
                fg_color="#1a1a1a",
                corner_radius=4,
                font=("Consolas", 10),
            )
            hex_lbl.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=2)

            dec_lbl = ctk.CTkLabel(
                scrollable_frame,
                text="0",
                fg_color="#1a1a1a",
                corner_radius=4,
                font=("Consolas", 10),
            )
            dec_lbl.grid(row=i + 1, column=2, sticky="ew", padx=5, pady=2)

            self.register_labels[reg_name] = (hex_lbl, dec_lbl)

        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=2)
        scrollable_frame.columnconfigure(2, weight=2)

    def update_registers(self, registers: list):
        """Actualiza la visualización de los registros"""
        for i in range(16):
            reg_name = f"R{i}"
            value = registers[i] if i < len(registers) else 0

            # Convertir a signed si es necesario
            if value >= 0x8000000000000000:
                signed_value = value - 0x10000000000000000
            else:
                signed_value = value

            hex_lbl, dec_lbl = self.register_labels[reg_name]
            hex_lbl.configure(text=f"0x{value:016X}")
            dec_lbl.configure(text=str(signed_value))
