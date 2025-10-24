import customtkinter as ctk


class FlagRegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.cpu = kwargs.get("cpu", None)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.flag_entries = {}

        self.__build_text()
        self.__build_table()

    def __build_text(self):
        title = ctk.CTkLabel(
            self, text="Flag register", font=("Comic Sans MS", 14), text_color="white"
        )
        title.grid(row=0, column=0)

    def __build_table(self):
        scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 10), pady=5)

        headers = ["Flag", "Value"]
        for j, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                scrollable_frame,
                text=header,
                fg_color="#2b2b2b",
                corner_radius=4,
                font=("Consolas", 12, "bold"),
            )
            lbl.grid(row=0, column=j, sticky="ew", padx=5, pady=5)

        # Crear etiquetas para cada flag
        flag_names = ["ZF", "SF", "CF", "OF"]
        for i, flag_name in enumerate(flag_names):
            name_lbl = ctk.CTkLabel(
                scrollable_frame,
                text=flag_name,
                fg_color="#2b2b2b",
                corner_radius=4,
                font=("Consolas", 11),
            )
            name_lbl.grid(row=i + 1, column=0, sticky="ew", padx=5, pady=2)

            value_entry = ctk.CTkEntry(
                scrollable_frame,
                fg_color="#1a1a1a",
                corner_radius=4,
                font=("Consolas", 11),
            )
            value_entry.insert(0, "0")
            value_entry.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=2)
            value_entry.bind(
                "<Return>", lambda e, name=flag_name: self.__on_flag_change(name)
            )
            value_entry.bind(
                "<FocusOut>", lambda e, name=flag_name: self.__on_flag_change(name)
            )

            self.flag_entries[flag_name] = value_entry

        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)

    def __on_flag_change(self, flag_name):
        """Aplica cambio cuando se edita un flag"""
        if not self.cpu:
            return

        flag_bits = {"ZF": 0, "SF": 1, "CF": 2, "OF": 3}
        entry = self.flag_entries[flag_name]
        value_str = entry.get().strip()

        try:
            value = int(value_str)
            if value not in [0, 1]:
                print(f"Valor inválido para {flag_name}: {value_str} (debe ser 0 o 1)")
                return

            bit_pos = flag_bits[flag_name]

            # Limpiar el bit
            self.cpu.flags &= ~(1 << bit_pos)
            # Establecer el nuevo valor
            self.cpu.flags |= value << bit_pos

        except ValueError:
            print(f"Valor inválido para {flag_name}: {value_str}")

    def update_flags(self, flags: int):
        """Actualiza la visualización de los flags"""
        zf = (flags >> 0) & 1
        sf = (flags >> 1) & 1
        cf = (flags >> 2) & 1
        of = (flags >> 3) & 1

        flag_values = {"ZF": zf, "SF": sf, "CF": cf, "OF": of}

        for flag_name, value in flag_values.items():
            entry = self.flag_entries[flag_name]
            entry.delete(0, "end")
            entry.insert(0, str(value))
