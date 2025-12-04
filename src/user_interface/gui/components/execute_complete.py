import customtkinter as ctk
from PIL import Image

from ..func import cpu_control
from .design_variable_elements import Fonts

class CompleteExecute(ctk.CTkFrame):
    def __init__(self, parent, fg_color = 'transparent', **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 0) # Label
        self.columnconfigure(3, weight = 1) # Entry
        self.rowconfigure(0, weight = 1)
        self.cpu = kwargs.get('cpu', None)
        self.update_callback = kwargs.get('update_callback', None)
        
        self.is_running = False
        self.execution_mode = None # 'delay' or 'complete'

        self.__makebutton()
        self.__tempo_switch()
        self.__tempo_value()
    
    def __makebutton(self):
        # ejecutar_completo_imagen = ctk.CTkImage(
        #     light_image = Image.open(),
        #     dark_image = Image.open(),
        #     size = (40, 40)
        # )
        self.ejecutar_completo = ctk.CTkButton(
            self, 
            text = 'Ejecutar completo',
            width=180,
            # image = ejecutar_completo_imagen,
            # compound = 'right',
            fg_color="#4C44AC",
            text_color="white",
            corner_radius=50,
            font=Fonts.get_font(""),
            command=self.__toggle_complete_execute
        )
        self.ejecutar_completo.grid(column=0, row=0, sticky="nsew", pady = 5, padx=5)
    

    def __tempo_switch(self):
        self.tempo_ejecutar = ctk.CTkButton(
            self,
            text = "Ejecutar con temporizador",
            width=220,
            fg_color="#4C44AC",
            text_color = "white",
            corner_radius=50,
            font=Fonts.get_font(""),
            command = self.__toggle_delay_execute
        )
        self.tempo_ejecutar.grid(column = 1, row = 0, sticky = "nsew", pady = 5, padx=5)
    

    def __tempo_value(self):
        # Label para indicar qué es el campo
        self.tempo_label = ctk.CTkLabel(
            self,
            text="Delay (s):",
            font=Fonts.get_font(""),
            text_color="white"
        )
        self.tempo_label.grid(column=2, row=0, sticky="e", padx=(5, 2))

        vcmd = (self.register(self.only_numbers), "%P")
        self.tempo_value = ctk.CTkEntry(
            self,
            placeholder_text = "1",
            font = Fonts.get_font(""),
            validate="key",
            validatecommand=vcmd
        )

        self.tempo_value.grid(column = 3, row = 0, sticky = "nsew", pady = 5, padx=5)
    
    def only_numbers(self, new_value):
        """Permite solo números vacíos o dígitos."""
        return new_value.isdigit() or new_value == ""
    
    def __toggle_delay_execute(self):
        if self.is_running:
            if self.execution_mode == 'delay':
                self.__stop_execution()
            return

        value = self.tempo_value.get()
        if value.isdigit() and value != "":
            delay_sec = int(value)
        else:
            delay_sec = 1
        
        delay_ms = delay_sec * 1000
        
        self.is_running = True
        self.execution_mode = 'delay'
        
        # Update UI
        self.tempo_ejecutar.configure(text="Detener ejecución", fg_color="#AA0000")
        self.ejecutar_completo.configure(state="disabled")
        
        self.__run_step_loop(delay_ms)

    def __toggle_complete_execute(self):
        if self.is_running:
            if self.execution_mode == 'complete':
                self.__stop_execution()
            return

        self.is_running = True
        self.execution_mode = 'complete'
        
        # Update UI
        self.ejecutar_completo.configure(text="Detener ejecución", fg_color="#AA0000")
        self.tempo_ejecutar.configure(state="disabled")
        
        # Run as fast as possible without freezing UI (1ms delay)
        self.__run_step_loop(1)

    def __stop_execution(self):
        self.is_running = False
        self.execution_mode = None
        
        # Restore UI
        self.tempo_ejecutar.configure(text="Ejecutar con temporizador", fg_color="#4C44AC", state="normal")
        self.ejecutar_completo.configure(text="Ejecutar completo", fg_color="#4C44AC", state="normal")

    def __run_step_loop(self, delay_ms):
        if not self.is_running:
            return

        # Execute one step
        should_continue = cpu_control.execute_step(self.cpu, self.update_callback)
        
        if should_continue:
            # Schedule next step
            self.after(delay_ms, lambda: self.__run_step_loop(delay_ms))
        else:
            # Program finished
            self.__stop_execution()