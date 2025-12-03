import customtkinter as ctk
from .design_variable_elements import Fonts

class RegistersWindow(ctk.CTkToplevel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.title("Registros y Flags")
        self.geometry("400x600")
        self.resizable(True, True)
        
        # State for throttling updates
        self.pending_state = None
        self.update_interval_ms = 200  # Update UI every 200ms to avoid lag
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0) # Toolbar
        self.rowconfigure(1, weight=0) # Flags title
        self.rowconfigure(2, weight=0) # Flags content
        self.rowconfigure(3, weight=0) # Registers title
        self.rowconfigure(4, weight=1) # Registers content

        self.flag_labels = {}
        self.register_labels = {}

        self.__build_ui()
        
        # Start the update loop
        self.after(self.update_interval_ms, self.__process_updates)
        
        # Handle window closing
        self.protocol("WM_DELETE_WINDOW", self.__on_close)
        self.is_open = True

    def __on_close(self):
        self.is_open = False
        self.withdraw()

    def show(self):
        self.deiconify()
        self.is_open = True

    def __build_ui(self):
        # --- Toolbar ---
        toolbar_frame = ctk.CTkFrame(self, fg_color="transparent", height=30)
        toolbar_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
        
        self.pin_switch = ctk.CTkSwitch(
            toolbar_frame, 
            text="Fijar ventana", 
            command=self.__toggle_topmost,
            font=Fonts.get_font("global_mini")
        )
        self.pin_switch.pack(side="right")

        # --- Flags Section ---
        ctk.CTkLabel(self, text="Flags", font=Fonts.get_font("global_mini"), text_color="white").grid(row=1, column=0, pady=(5, 5))
        
        flags_frame = ctk.CTkFrame(self, fg_color="transparent")
        flags_frame.grid(row=2, column=0, sticky="ew", padx=10)
        
        flag_names = ["ZF", "SF", "CF", "OF"]
        for i, name in enumerate(flag_names):
            flags_frame.columnconfigure(i, weight=1)
            frame = ctk.CTkFrame(flags_frame, fg_color="#2b2b2b")
            frame.grid(row=0, column=i, padx=2, sticky="ew")
            
            ctk.CTkLabel(frame, text=name, font=Fonts.get_font("consolas_mini")).pack(side="top")
            lbl = ctk.CTkLabel(frame, text="0", font=Fonts.get_font("consolas_mini"), text_color="#00ff00")
            lbl.pack(side="bottom")
            self.flag_labels[name] = lbl

        # --- Registers Section ---
        ctk.CTkLabel(self, text="Registros de Propósito General", font=Fonts.get_font("global_mini"), text_color="white").grid(row=3, column=0, pady=(20, 5))

        regs_scroll = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        regs_scroll.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        regs_scroll.columnconfigure(0, weight=0) # Name
        regs_scroll.columnconfigure(1, weight=1) # Hex
        regs_scroll.columnconfigure(2, weight=1) # Dec

        # Headers
        headers = ["Reg", "Hex", "Dec"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(regs_scroll, text=h, font=Fonts.get_font("consolas_mini"), fg_color="#2b2b2b", corner_radius=4).grid(row=0, column=i, sticky="ew", padx=2, pady=2)

        # Rows
        for i in range(16):
            reg_name = f"R{i}"
            ctk.CTkLabel(regs_scroll, text=reg_name, font=Fonts.get_font("consolas"), fg_color="#2b2b2b", corner_radius=4).grid(row=i+1, column=0, sticky="ew", padx=2, pady=2)
            
            hex_lbl = ctk.CTkLabel(regs_scroll, text="0x0000000000000000", font=Fonts.get_font("consolas"), anchor="e")
            hex_lbl.grid(row=i+1, column=1, sticky="ew", padx=5)
            
            dec_lbl = ctk.CTkLabel(regs_scroll, text="0", font=Fonts.get_font("consolas"), anchor="e")
            dec_lbl.grid(row=i+1, column=2, sticky="ew", padx=5)
            
            self.register_labels[reg_name] = (hex_lbl, dec_lbl)

    def __toggle_topmost(self):
        is_pinned = self.pin_switch.get() == 1
        self.attributes('-topmost', is_pinned)

    def update_state(self, state):
        """Queue an update with the latest state."""
        if self.is_open:
            self.pending_state = state

    def __process_updates(self):
        if self.is_open and self.pending_state:
            state = self.pending_state
            self.pending_state = None # Clear pending state
            
            if "flags" in state:
                self.__update_flags_ui(state["flags"])
            
            if "registers" in state:
                self.__update_registers_ui(state["registers"])
        
        # Schedule next check
        self.after(self.update_interval_ms, self.__process_updates)

    def __update_flags_ui(self, flags):
        zf = (flags >> 0) & 1
        sf = (flags >> 1) & 1
        cf = (flags >> 2) & 1
        of = (flags >> 3) & 1
        
        vals = {"ZF": zf, "SF": sf, "CF": cf, "OF": of}
        for name, val in vals.items():
            self.flag_labels[name].configure(text=str(val))

    def __update_registers_ui(self, registers):
        for i in range(16):
            reg_name = f"R{i}"
            value = registers[i] if i < len(registers) else 0
            
            # Signed conversion
            if value >= 0x8000000000000000:
                signed_value = value - 0x10000000000000000
            else:
                signed_value = value
                
            hex_lbl, dec_lbl = self.register_labels[reg_name]
            hex_lbl.configure(text=f"0x{value:016X}")
            dec_lbl.configure(text=str(signed_value))
