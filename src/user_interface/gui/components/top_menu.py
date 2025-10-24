"""
Nombre del archivo: top_menu.py
Descripción: Este módulo es el frame de la parte superior de la interfaz gráfica en donde
             se tiene el logo y el menú de opciones.
Autor: Camilo Medina
Fecha: 07/10/2025
Versión: 1.0
"""

import customtkinter as ctk
from PIL import Image


class TopMenuTitleOptions(ctk.CTkFrame):
    def __init__(self, parent, height, width, **kwargs):
        super().__init__(parent, width=width, height=height, fg_color="transparent")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.logo_path = kwargs.get("logo_path", "")
        self.home = kwargs.get("home")
        self.help = kwargs.get("help")
        self.info = kwargs.get("info")
        self.iconos_menu = [self.home, self.help, self.info]
        self.logo_width = kwargs.get("image_width", 40)
        self.logo_height = kwargs.get("image_height", 40)

        self.__build_left_section()
        self.__build_right_section()

    def __build_left_section(self):
        contenedor_titulo = ctk.CTkFrame(self, fg_color="transparent")

        contenedor_titulo.columnconfigure(0, weight=1)
        contenedor_titulo.columnconfigure(1, weight=1)
        contenedor_titulo.rowconfigure(0, weight=1)
        contenedor_titulo.rowconfigure(1, weight=1)

        logo_image = ctk.CTkImage(
            light_image=Image.open(self.logo_path),
            dark_image=Image.open(self.logo_path),
            size=(self.logo_width, self.logo_height),
        )

        logo_label = ctk.CTkLabel(contenedor_titulo, image=logo_image, text="")
        logo_label.grid(row=0, column=0, rowspan=2, sticky="w")

        title_label = ctk.CTkLabel(
            contenedor_titulo,
            text="ΣUCLID-64",
            font=("Comic Sans MS", 30, "bold"),
            text_color="white",
        )
        title_label.grid(row=0, column=1, sticky="w")

        factory_label = ctk.CTkLabel(
            contenedor_titulo,
            text="peñatech - labs",
            font=("Comic Sans MS", 14),
            text_color="white",
        )
        factory_label.grid(row=1, column=1, sticky="w")

        contenedor_titulo.grid(row=0, column=0, sticky="w", padx=(20, 0))

    def __build_right_section(self):
        contenedor_opciones = ctk.CTkFrame(self, corner_radius=60, fg_color="#0C1826")

        contenedor_opciones.rowconfigure(0, weight=1)
        contenedor_opciones.columnconfigure(0, weight=1)
        contenedor_opciones.columnconfigure(1, weight=1)
        contenedor_opciones.columnconfigure(2, weight=1)

        for _ in range(len(self.iconos_menu)):
            try:
                icon_img = ctk.CTkImage(
                    light_image=Image.open(self.iconos_menu[_]),
                    dark_image=Image.open(self.iconos_menu[_]),
                    size=(self.logo_width, self.logo_height),
                )
                icon_label = ctk.CTkLabel(
                    contenedor_opciones,
                    image=icon_img,
                    text="",
                    fg_color="transparent",
                    cursor="hand2",
                )
                icon_label.image = icon_img
                icon_label.grid(row=0, column=_, padx=45)
            except:
                pass

        contenedor_opciones.grid(row=0, column=1, sticky="e", padx=(0, 35))
