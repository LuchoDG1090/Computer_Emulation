import customtkinter as ctk


class FlagRegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826"):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.flag_labels = {}

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

            value_lbl = ctk.CTkLabel(
                scrollable_frame,
                text="0",
                fg_color="#1a1a1a",
                corner_radius=4,
                font=("Consolas", 11),
            )
            value_lbl.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=2)

            self.flag_labels[flag_name] = value_lbl

        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)

    def update_flags(self, flags: int):
        """Actualiza la visualización de los flags"""
        zf = (flags >> 0) & 1
        sf = (flags >> 1) & 1
        cf = (flags >> 2) & 1
        of = (flags >> 3) & 1

        self.flag_labels["ZF"].configure(text=str(zf))
        self.flag_labels["SF"].configure(text=str(sf))
        self.flag_labels["CF"].configure(text=str(cf))
        self.flag_labels["OF"].configure(text=str(of))
