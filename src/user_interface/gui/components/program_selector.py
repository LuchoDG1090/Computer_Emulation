import customtkinter as ctk

from ..func.compilation_registry import CompilationRegistry


class ProgramSelectorFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.cpu = kwargs.get("cpu", None)
        self.pc_update_callback = kwargs.get("pc_update_callback", None)
        self.update_state_callback = kwargs.get("update_state_callback", None)
        self.memory = kwargs.get("memory", None)
        self.ram_display = kwargs.get("ram_display", None)
        self._label_to_program = {}

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)

        self.__build_label()
        self.__build_selector()
        self.__build_unload_button()

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

    def __build_unload_button(self):
        """Botón para descargar el programa seleccionado"""
        unload_button = ctk.CTkButton(
            self,
            text="X",
            fg_color="#DC3545",
            text_color="white",
            width=30,
            font=("Comic Sans MS", 12, "bold"),
            command=self.__unload_selected_program,
        )
        unload_button.grid(row=0, column=2, padx=5, pady=5)

    def __unload_selected_program(self):
        """Descarga el programa actualmente seleccionado"""
        selected_label = self.selector.get()
        if selected_label == "Ninguno":
            return

        # Obtener el programa exacto por etiqueta
        program = self._label_to_program.get(selected_label)
        if program and self.memory:
            # Limpiar memoria del programa
            for addr in range(program.min_addr, program.max_addr + 1, 8):
                self.memory.write_word(addr, 0)
            print(
                f"Memoria limpiada: {program.min_addr // 8} - {program.max_addr // 8}"
            )

        # Eliminar solo esta instancia
        CompilationRegistry.unload_program_instance(program)
        print(f"Programa '{selected_label}' descargado")

        # Actualizar visualización de RAM con programas restantes
        if self.ram_display:
            remaining_programs = CompilationRegistry.get_loaded_programs()
            if remaining_programs:
                # Mostrar el primer programa restante
                first = remaining_programs[0]
                self.ram_display.update_memory(
                    self.memory, first.min_addr, first.max_addr
                )
            else:
                self.ram_display.clear_memory()

        self.update_program_list()

    def update_program_list(self):
        """Actualiza la lista de programas cargados"""
        programs = CompilationRegistry.get_loaded_programs()
        self._label_to_program = {}
        if programs:
            labels = []
            for p in programs:
                label = f"{p.name} @ {p.entry_point // 8}"
                original = label
                k = 2
                while label in self._label_to_program:
                    label = f"{original} ({k})"
                    k += 1
                self._label_to_program[label] = p
                labels.append(label)
            self.selector.configure(values=labels)
            if len(labels) == 1:
                self.selector.set(labels[0])
                self.__on_program_selected(labels[0])
        else:
            self.selector.configure(values=["Ninguno"])
            self.selector.set("Ninguno")

    def __on_program_selected(self, selected_label):
        """Configura el CPU para ejecutar el programa seleccionado."""
        if not self.cpu:
            print("No hay CPU disponible para configurar.")
            return

        program = self._label_to_program.get(selected_label)
        if not program:
            print(f"Programa '{selected_label}' no encontrado.")
            return

        self.__configure_cpu_for_program(program)

    def __find_program_by_name(self, name):
        """Compatibilidad temporal: búsqueda por nombre (puede devolver el primero si hay duplicados)."""
        programs = CompilationRegistry.get_loaded_programs()
        return next((p for p in programs if p.name == name), None)

    def __configure_cpu_for_program(self, program):
        """Inicializa los registros del CPU para ejecutar el programa dado."""
        self.cpu.pc = program.entry_point
        self.cpu.ir = 0
        self.cpu.flags = 0
        self.cpu.registers.reset()
        self.cpu.stack_ops.reset()
        self.cpu.running = False
        self.cpu.cycle_count = 0

        word_pos = program.entry_point // 8
        print(f"CPU configurado para ejecutar '{program.name}' desde PC={word_pos}")

        if self.pc_update_callback:
            self.pc_update_callback(program.entry_point)

        if self.update_state_callback:
            self.update_state_callback(self.cpu.get_state())
