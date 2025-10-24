import customtkinter as ctk
from PIL import Image

from src.user_interface.gui.func import reloc as func


class RelocCodeFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0C1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.reloc_icon = kwargs.get("reloc_icon", "")
        self.cpu = kwargs.get("cpu", "")
        self.memory = kwargs.get("memory", "")
        self.ram_display = kwargs.get("ram_display", None)
        self.program_selector = kwargs.get("program_selector", None)

        self.__build_text()
        self.__build_entry_text()
        self.__build_address_input()
        self.__build_buttons()

    def __build_text(self):
        text = ctk.CTkLabel(
            self,
            text="Código relocalizable",
            font=("Comic Sans MS", 14),
            text_color="white",
        )
        text.grid(row=0, column=0)

    def __build_entry_text(self):
        self.text_entry = ctk.CTkTextbox(self, fg_color="#2b2b2b")
        self.text_entry.grid(row=1, column=0, sticky="nsew", padx=12)

    def __build_address_input(self):
        """Campo para especificar dirección base de carga"""
        addr_frame = ctk.CTkFrame(self, fg_color="transparent")
        addr_frame.columnconfigure(0, weight=1)
        addr_frame.columnconfigure(1, weight=2)
        addr_frame.columnconfigure(2, weight=1)
        addr_frame.columnconfigure(3, weight=2)

        label = ctk.CTkLabel(
            addr_frame,
            text="Dirección base (decimal):",
            font=("Comic Sans MS", 12),
            text_color="white",
        )
        label.grid(row=0, column=0, sticky="e", padx=5)

        self.address_entry = ctk.CTkEntry(
            addr_frame, placeholder_text="0 (suma a direcciones)", font=("Consolas", 11)
        )
        self.address_entry.grid(row=0, column=1, sticky="ew", padx=5)

        # Nombre personalizado del programa (opcional)
        name_label = ctk.CTkLabel(
            addr_frame,
            text="Nombre:",
            font=("Comic Sans MS", 12),
            text_color="white",
        )
        name_label.grid(row=0, column=2, sticky="e", padx=5)

        self.program_name_entry = ctk.CTkEntry(
            addr_frame, placeholder_text="Opcional", font=("Consolas", 11)
        )
        self.program_name_entry.grid(row=0, column=3, sticky="ew", padx=5)

        addr_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=5)

    def __build_buttons(self):
        button_frame = ctk.CTkFrame(self, fg_color="transparent")

        button_frame.columnconfigure(0, weight=1)
        button_frame.rowconfigure(0, weight=1)

        compile_image = ctk.CTkImage(
            light_image=Image.open(self.reloc_icon),
            dark_image=Image.open(self.reloc_icon),
            size=(40, 40),
        )
        boton_enlazar_cargar = ctk.CTkButton(
            button_frame,
            text="Enlazar-cargar",
            image=compile_image,
            compound="right",
            fg_color="#4C44AC",
            text_color="white",
            corner_radius=50,
            font=("Comic Sans MS", 16, "bold"),
            command=lambda: self.__link_load_and_update(),
        )
        boton_enlazar_cargar.grid(row=0, column=0)

        button_frame.grid(column=0, row=3, sticky="nsew", padx=30)

    def set_text(self, text):
        self.text_entry.delete("1.0", "end")
        self.text_entry.insert("1.0", text)

    def __link_load_and_update(self):
        """Carga el programa y actualiza el selector"""
        # Obtener dirección base si se especificó
        base_address = None
        addr_text = self.address_entry.get().strip()
        if addr_text:
            try:
                # Interpretar como posición de palabra en decimal
                word_position = int(addr_text)
                # Convertir a bytes (multiplicar por 8)
                base_address = word_position * 8

            except ValueError:
                print(f"\033[31m Error: dirección inválida '{addr_text}' \033[0m")
                return

        # Obtener nombre personalizado si se proporcionó
        program_name = self.program_name_entry.get().strip()
        if program_name == "":
            program_name = None

        func.link_load(
            self.text_entry, self.memory, self.ram_display, base_address, program_name
        )
        if self.program_selector:
            self.program_selector.update_program_list()
