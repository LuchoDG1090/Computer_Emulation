"""
Nombre del archivo: main_func.py
Descripción: Este módulo es el frame que permite tener las funcionalidades de toda la emulación.
             Acá se agrupan todos los módulos individuales
Versión: 1.0
"""

import customtkinter as ctk

from src.user_interface.gui.components import (
    assembly,
    buttons_actions,
    console,
    execute_complete,
    high_level_code,
    program_counter,
    program_selector,
    ram,
    reloc,
    registers_window,
)
from .design_variable_elements import Fonts


class MainFunctionalityMenu(ctk.CTkFrame):
    def __init__(self, parent, height, width, **kwargs):
        super().__init__(parent, width=width, height=height, fg_color="transparent")

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=5)
        self.rowconfigure(0, weight=1)
        # Crear el selector de programas primero para poder pasarlo a reloc
        self.program_selector = None
        self.memory = kwargs.get("memory", "")
        self.cpu = kwargs.get("cpu", "")
        self.compile_icon_path = kwargs.get("compile_icon_path", "")
        self.upload_icon_path = kwargs.get("upload_icon_path", "")
        self.assemble_icon_path = kwargs.get("assemble_icon_path", "")
        self.reloc_icon_path = kwargs.get("reloc_icon_path", "")
        self.siguiente_icon_path = kwargs.get("siguiente_icon_path", "")
        self.reiniciar_icon_path = kwargs.get("reiniciar_icon_path", "")
        self.clean_iconpath = kwargs.get("clean_icon_path", "")

        self.__build_second_column()
        self.__build_first_column()
        self.__build_third_column()

    def __build_first_column(self):
        frame_first_column = ctk.CTkFrame(self, fg_color="transparent")

        frame_first_column.rowconfigure(0, weight=1)
        frame_first_column.rowconfigure(1, weight=1)
        frame_first_column.columnconfigure(0, weight=1)

        high_level_code_section = high_level_code.HighLevelCodeFrame(
            frame_first_column,
            compile_icon=self.compile_icon_path,
            upload_icon=self.upload_icon_path,
            clean_icon=self.clean_iconpath,
        )
        high_level_code_section.grid(column=0, row=0, sticky="nsew", pady=12)

        assembly_frame = assembly.AssemblyCodeFrame(
            frame_first_column,
            upload_icon=self.upload_icon_path,
            assemble_icon=self.assemble_icon_path,
            clean_icon=self.clean_iconpath,
            funcion_set=self.reloc_code.set_text,
        )
        assembly_frame.grid(column=0, row=1, sticky="nsew", pady=12)
        
        # Conectar el callback de compilación para actualizar el frame de assembly
        high_level_code_section.set_assembly_callback(assembly_frame.set_text)

        frame_first_column.grid(
            column=0, row=0, sticky="nsew", padx=(10, 10), pady=(10, 10)
        )

    def __build_second_column(self):
        self.frame_second_column = ctk.CTkFrame(self, fg_color="transparent")
        # Distribución: Reloc (arriba), RAM (principal ocupa casi todo),
        # bloque inferior compacto (selector + PC + Ejecutar completo)
        self.frame_second_column.rowconfigure(0, weight=2, minsize=100)
        self.frame_second_column.rowconfigure(1, weight=7, minsize=260)
        self.frame_second_column.rowconfigure(2, weight=0, minsize=120)
        self.frame_second_column.columnconfigure(0, weight=1)

        self.ram_memory = ram.DinamicRandomAccessMemory(
            self.frame_second_column,
            memory=self.memory,
            cpu=self.cpu,
            apply_icon=self.assemble_icon_path,
            load_icon=self.upload_icon_path,
        )

        self.reloc_code = reloc.RelocCodeFrame(
            self.frame_second_column,
            reloc_icon=self.reloc_icon_path,
            memory=self.memory,
            cpu=self.cpu,
            ram_display=self.ram_memory,
            program_selector=None,  # Se configurará después
        )

        self.frame_pc_selector_programa = ctk.CTkFrame(
            self.frame_second_column, fg_color="transparent"
        )
        # Bloque inferior compacto, sin expansión vertical
        self.frame_pc_selector_programa.rowconfigure(0, weight=0, minsize=36)
        self.frame_pc_selector_programa.rowconfigure(1, weight=0, minsize=36)
        self.frame_pc_selector_programa.rowconfigure(2, weight=0, minsize=44)
        self.frame_pc_selector_programa.columnconfigure(0, weight=1)

        # Program Counter (crear antes del selector para poder pasar el callback)
        self.pc_frame = program_counter.ProgramCounterFrame(
            self.frame_pc_selector_programa, cpu=self.cpu
        )

        # Crear el selector y conectarlo con reloc
        self.program_selector = program_selector.ProgramSelectorFrame(
            self.frame_pc_selector_programa,
            cpu=self.cpu,
            pc_update_callback=self.pc_frame.update_pc,
            update_state_callback=self.__update_cpu_state,
            memory=self.memory,
            ram_display=self.ram_memory,
        )

        self.execute_complete = execute_complete.CompleteExecute(
            self.frame_pc_selector_programa,
            cpu=self.cpu,
            update_callback=self.__update_cpu_state,
        )

        # Ubicar frames en la segunda columna
        self.pc_frame.grid(column=0, row=0, sticky="nsew")
        self.program_selector.grid(column=0, row=1, sticky="nsew")
        self.execute_complete.grid(column=0, row=2, sticky="ew", pady=(6, 0))

        self.reloc_code.grid(column=0, row=0, sticky="nsew", pady=12)
        self.ram_memory.grid(column=0, row=1, sticky="nsew", pady=12)
        self.frame_pc_selector_programa.grid(column=0, row=2, sticky="nsew", pady=12)

        # Conectar callback de actualización de PC al visor de RAM
        if hasattr(self.ram_memory, "set_pc_update_callback"):
            self.ram_memory.set_pc_update_callback(self.pc_frame.update_pc)

        # Conectar referencia al selector de programas en RAM
        if hasattr(self.ram_memory, "set_program_selector"):
            self.ram_memory.set_program_selector(self.program_selector)

        self.frame_second_column.grid(
            column=1, row=0, sticky="nsew", padx=(10, 10), pady=(10, 10)
        )

    def __build_third_column(self):
        frame_third_column = ctk.CTkFrame(self, fg_color="transparent")

        frame_third_column.rowconfigure(0, weight=1)
        frame_third_column.rowconfigure(1, weight=0)
        frame_third_column.rowconfigure(2, weight=0)
        frame_third_column.grid_propagate(False)
        frame_third_column.columnconfigure(0, weight=1)

        self.console_frame = console.ConsoleFrame(frame_third_column)
        
        # Initialize registers window lazily
        self.registers_window = None

        self.reloc_code.program_selector = self.program_selector
        self.program_selector.set_clear_console_callback(self.console_frame.clear_console)

        botones_acciones = buttons_actions.BotonesAcciones(
            frame_third_column,
            imagen_siguiente=self.siguiente_icon_path,
            reiniciar_imagen=self.reiniciar_icon_path,
            cpu=self.cpu,
            update_callback=self.__update_cpu_state,
            clear_output_callback=self.console_frame.clear_console,
            clear_ram_callback=self.ram_memory.clear_memory,
            console_frame=self.console_frame,
            clear_programs_callback=self.program_selector.update_program_list,
        )
        
        btn_show_regs = ctk.CTkButton(
            frame_third_column, 
            text="Ver Registros y Flags", 
            command=self.__show_registers_window,
            font=Fonts.get_font("global_mini"),
            fg_color="#4C44AC",
            text_color="white",
            corner_radius=50
        )

        self.console_frame.grid(column=0, row=0, sticky="nsew", pady=12)
        btn_show_regs.grid(column=0, row=1, sticky="ew", pady=(0, 12))
        botones_acciones.grid(column=0, row=2, sticky="ew", pady=12)

        frame_third_column.grid(
            column=2, row=0, sticky="nsew", padx=(10, 10), pady=(10, 10)
        )

        # Conectar callbacks de I/O del CPU
        self.__setup_io_callbacks()

    def __show_registers_window(self):
        if self.registers_window is None:
            self.registers_window = registers_window.RegistersWindow(self)
        self.registers_window.show()

    def __setup_io_callbacks(self):
        """Configura los callbacks de entrada/salida del CPU"""
        if self.cpu:
            # Callbacks de salida
            self.cpu.io_ports.set_output_char_callback(self.console_frame.append_char)
            self.cpu.io_ports.set_output_int_callback(self.console_frame.append_int)

            # Callbacks de entrada
            self.cpu.io_ports.set_input_char_callback(self.console_frame.request_char)
            self.cpu.io_ports.set_input_int_callback(self.console_frame.request_int)
            self.cpu.io_ports.set_input_line_callback(self.console_frame.request_line)

    def __update_cpu_state(self, state):
        """
        Actualiza todos los componentes de la GUI con el estado del CPU

        Args:
            state: Diccionario con el estado del CPU
        """
        # Actualizar registros y flags en la nueva ventana
        if hasattr(self, "registers_window") and self.registers_window:
            self.registers_window.update_state(state)

        # Actualizar PC
        if "pc" in state:
            self.pc_frame.update_pc(state["pc"])

        # Refrescar la vista de RAM con los valores actuales de memoria, sin
        # perder ediciones en curso. Esto permite ver inmediatamente los cambios
        # en memoria producidos por instrucciones como IN/LD/ST, E/S, etc.
        if hasattr(self, "ram_memory") and self.ram_memory is not None:
            try:
                self.ram_memory.refresh_visible()
            except Exception:
                # Si aún no hay un rango mostrado o el widget no está listo, ignorar.
                pass
