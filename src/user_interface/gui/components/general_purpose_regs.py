import customtkinter as ctk


class GeneralPurposeRegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0C1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.cpu = kwargs.get("cpu", None)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.register_entries = {}

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

            hex_entry = ctk.CTkEntry(
                scrollable_frame,
                fg_color="#1a1a1a",
                corner_radius=4,
                font=("Consolas", 10),
            )
            hex_entry.insert(0, "0x0000000000000000")
            hex_entry.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=2)
            hex_entry.bind("<Return>", lambda e, idx=i: self.__on_hex_change(idx))
            hex_entry.bind("<FocusOut>", lambda e, idx=i: self.__on_hex_change(idx))

            dec_entry = ctk.CTkEntry(
                scrollable_frame,
                fg_color="#1a1a1a",
                corner_radius=4,
                font=("Consolas", 10),
            )
            dec_entry.insert(0, "0")
            dec_entry.grid(row=i + 1, column=2, sticky="ew", padx=5, pady=2)
            dec_entry.bind("<Return>", lambda e, idx=i: self.__on_dec_change(idx))
            dec_entry.bind("<FocusOut>", lambda e, idx=i: self.__on_dec_change(idx))

            self.register_entries[reg_name] = (hex_entry, dec_entry)

        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=2)
        scrollable_frame.columnconfigure(2, weight=2)

    def __on_hex_change(self, reg_index):
        """Aplica cambio cuando se edita el campo hexadecimal"""
        if not self.cpu:
            return

        reg_name = f"R{reg_index}"
        hex_entry, dec_entry = self.register_entries[reg_name]

        try:
            hex_value = hex_entry.get().strip()
            if hex_value.startswith("0x") or hex_value.startswith("0X"):
                hex_value = hex_value[2:]

            value = int(hex_value, 16)

            if value < 0 or value > 0xFFFFFFFFFFFFFFFF:
                print(f"Valor fuera de rango para {reg_name}: {hex_value}")
                return

            self.cpu.registers.write(reg_index, value)

            # Actualizar campo decimal
            if value >= 0x8000000000000000:
                signed_value = value - 0x10000000000000000
            else:
                signed_value = value

            dec_entry.delete(0, "end")
            dec_entry.insert(0, str(signed_value))

        except ValueError:
            print(f"Valor hexadecimal inválido para {reg_name}: {hex_entry.get()}")

    def __on_dec_change(self, reg_index):
        """Aplica cambio cuando se edita el campo decimal"""
        if not self.cpu:
            return

        reg_name = f"R{reg_index}"
        hex_entry, dec_entry = self.register_entries[reg_name]

        try:
            signed_value = int(dec_entry.get().strip())

            # Convertir a unsigned de 64 bits
            if signed_value < 0:
                value = signed_value + 0x10000000000000000
            else:
                value = signed_value

            if value < 0 or value > 0xFFFFFFFFFFFFFFFF:
                print(f"Valor fuera de rango para {reg_name}: {signed_value}")
                return

            self.cpu.registers.write(reg_index, value)

            # Actualizar campo hexadecimal
            hex_entry.delete(0, "end")
            hex_entry.insert(0, f"0x{value:016X}")

        except ValueError:
            print(f"Valor decimal inválido para {reg_name}: {dec_entry.get()}")

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

            hex_entry, dec_entry = self.register_entries[reg_name]

            # Actualizar campos de entrada
            hex_entry.delete(0, "end")
            hex_entry.insert(0, f"0x{value:016X}")

            dec_entry.delete(0, "end")
            dec_entry.insert(0, str(signed_value))
