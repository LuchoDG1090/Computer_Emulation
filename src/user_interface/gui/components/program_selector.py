import customtkinter as ctk

from ..func.compilation_registry import CompilationRegistry


class ProgramSelectorFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.cpu = kwargs.get("cpu", None)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.__build_label()
        self.__build_selector()

    def __build_label(self):
        label = ctk.CTkLabel(
            self,
            text="Programa a ejecutar:",
            text_color="white",
            font=("Comic Sans MS", 12),
        )
        label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    def __build_selector(self):
        self.selector = ctk.CTkComboBox(
            self,
            values=["Ninguno"],
            state="readonly",
            command=self.__on_program_selected,
        )
        self.selector.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.selector.set("Ninguno")

    def update_program_list(self):
        """Actualiza la lista de programas cargados"""
        programs = CompilationRegistry.get_loaded_programs()
        if programs:
            program_names = [p.name for p in programs]
            self.selector.configure(values=program_names)
            if len(programs) == 1:
                self.selector.set(program_names[0])
                self.__on_program_selected(program_names[0])
        else:
            self.selector.configure(values=["Ninguno"])
            self.selector.set("Ninguno")

    def __on_program_selected(self, selected_name):
        """Configura el CPU para ejecutar el programa seleccionado"""
        programs = CompilationRegistry.get_loaded_programs()
        for program in programs:
            if program.name == selected_name:
                if self.cpu:
                    self.cpu.pc = program.entry_point
                    print(
                        f"CPU configurado para ejecutar '{selected_name}' desde PC=0x{program.entry_point:x}"
                    )
                break
