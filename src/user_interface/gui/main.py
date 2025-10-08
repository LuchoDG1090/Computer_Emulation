#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import customtkinter as ctk
from components import top_menu, main_func

class Routes:
    LOGO_PATH = r"resources\logo_sin_fondo.png"
    HOME_PATH = r"resources\home.png"
    HELP_PATH = r"resources\help.png"
    INFO_PATH = r"resources\information.png"
    COMPILE_ICON_PATH = r'resources\compilador.png'
    UPLOAD_ICON_PATH = r'resources\upload.png'
    ASSEMBLE_ICON_PATH = r'resources\assemble.png'
    RELOC_ICON_PATH = r'resources\enlazar-cargar.png'


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

        main_functionality_frame = main_func.MainFunctionalityMenu(
            self,
            self.__return_percentage_relation(self.height, 90),
            self.width,
            compile_icon_path = Routes.COMPILE_ICON_PATH,
            upload_icon_path = Routes.UPLOAD_ICON_PATH,
            assemble_icon_path = Routes.ASSEMBLE_ICON_PATH,
            reloc_icon_path = Routes.RELOC_ICON_PATH
        )
        main_functionality_frame.grid(row = 1, column = 0, sticky = 'nsew')

    def __return_percentage_relation(self, dimension, percentage):
        return (dimension * percentage) / 100

if __name__ == '__main__':
    app = MainFrame()
    app.mainloop()