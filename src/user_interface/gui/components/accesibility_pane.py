import customtkinter as ctk

from .design_variable_elements import *


class AccesibilityPanel(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Personalización")
        self.lift()
        self.focus_force()
        self.grab_set()
        self.resizable(False, False)
        # self.after(10, self.__center)
        self.geometry("400x300")
        self.__font_family_selector()
        self.__font_size_slider()
        self.__font_weight()
        self.__color_picker()

    def __font_family_selector(self):
        ctk.CTkLabel(self, text="Familia de la letra:").pack(pady=(10,5))
        self.font_family_option_menu = ctk.CTkOptionMenu(
            self,
            values = available_fonts,
            command = self.update_font
        )
        self.font_family_option_menu.set(global_font)
        self.font_family_option_menu.pack()
    

    def __font_size_slider(self):
        ctk.CTkLabel(self, text = "Tamaño de la letra").pack(pady=(10,5))
        self.font_size = ctk.CTkSlider(
            self,
            from_ = MIN_FONT_SIZE,
            to = MAX_FONT_SIZE,
            number_of_steps = (MAX_FONT_SIZE - MIN_FONT_SIZE),
            command = self.update_font
        )
        self.font_size.set(global_size)
        self.font_size.pack(fill = "x", padx=20)

    
    def __font_weight(self):
        ctk.CTkLabel(self, text = "Peso:").pack(pady=(10,5))
        self.font_weight = ctk.CTkOptionMenu(
            self, 
            values = available_weight,
            command = self.update_font
        )
        self.font_weight.set(global_weight)
        self.font_weight.pack()
    
    def __color_picker(self):
        ctk.CTkLabel(self, text="Color del texto:").pack(pady=(10, 5))
        self.color_entry = ctk.CTkEntry(self)
        self.color_entry.insert(0, global_text_color)
        self.color_entry.pack()
        ctk.CTkButton(self, text="Aplicar color", command=self.update_color).pack(pady=10)
    
    def update_font(self, _=None):
        global global_font_family, global_font_size, global_font_weight

        global_font_family = self.font_family_option_menu.get()
        global_font_size = int(self.font_size.get())
        global_font_weight = self.font_weight.get()

        Fonts.configure(
            family=global_font_family,
            size=global_font_size,
            weight=global_font_weight
        )

        # print(Fonts.family)
        # print(Fonts.size)
        # print(Fonts.weight)

    
    def __center(self):
        self.update_idletasks()
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_w = self.master.winfo_width()
        master_h = self.master.winfo_height()

        w = self.winfo_width()
        h = self.winfo_height()

        x = master_x + (master_w // 2) - (w // 2)
        y = master_y + (master_h // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")

