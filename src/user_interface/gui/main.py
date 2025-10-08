#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import customtkinter as ctk
from components import top_menu

class Routes:
    LOGO_PATH = r"resources\logo_sin_fondo.png"
    HOME_PATH = r"resources\home.png"
    HELP_PATH = r"resources\help.png"
    INFO_PATH = r"resources\information.png"


class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title = 'Euclid-64 emulation'
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry(f'{self.width}x{self.height}')

        self.configure(fg_color = '#26205E')

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=9)
        self.columnconfigure(0, weight=1)

        # # Top Menu
        # self.top_menu = ctk.CTkFrame(self, fg_color="#1a1a1a")
        # self.top_menu.grid(row=0, column=0, sticky="nsew")
        # self.top_menu.columnconfigure(0, weight=1)

        title_section = top_menu.TopMenuTitleOptions(
            self,
            self.__return_percentage_relation(self.height, 10),
            self.width,
            logo_path = Routes.LOGO_PATH,
            home = Routes.HOME_PATH,
            help = Routes.HELP_PATH,
            info = Routes.INFO_PATH,
            image_width = self.__return_percentage_relation(self.height, 10),
            image_height = self.__return_percentage_relation(self.height, 10)
        )

        title_section.grid(row=0, column=0, sticky="nsew")


        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        

        
    
    def __return_percentage_relation(self, dimension, percentage):
        return (dimension * percentage) / 100

if __name__ == '__main__':
    app = MainFrame()
    app.mainloop()