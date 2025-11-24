import customtkinter as ctk

available_fonts = [
    "Comic Sans MS", "Arial", "Helvetica",
    "Calibri", "Segoe UI", "Times New Roman",
    "Verdana", "Courier New"
]

available_weight = ["normal", "bold"]

MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 60

global_font = "Arial"
global_size = 16
global_weight = "bold"
global_text_color = "white"


class Fonts:
    # FUENTES
    global_font = None
    global_font_plus = None
    consolas_mini = None
    consolas = None
    global_font_mini = None
    # SPECS
    family = global_font
    size = global_size
    weight = global_weight

    @staticmethod
    def init_fonts():
        """Inicializa la fuente global al arrancar la aplicación."""
        Fonts.global_font = ctk.CTkFont(
            family=Fonts.family,
            size=Fonts.size,
            weight=Fonts.weight
        )
        Fonts.global_font_plus = ctk.CTkFont(
            family = Fonts.family,
            size=Fonts.size + 2,
            weight=Fonts.weight
        )
        Fonts.consolas = ctk.CTkFont(
            family = "Consolas",
            size = 12,
            weight = "normal"
        )
        Fonts.consolas_mini = ctk.CTkFont(
            family = "Consolas", 
            size = 10,
            weight =  "normal"
        )
        Fonts.global_font_mini = ctk.CTkFont(
            family = Fonts.family,
            size=Fonts.size - 2,
            weight=Fonts.weight
        )

    @staticmethod
    def configure(family=None, size=None, weight=None):
        """
        Actualiza dinámicamente la fuente global.
        Todos los widgets que usen Fonts.global_font cambiarán automáticamente.
        """

        if Fonts.global_font is None:
            Fonts.init_fonts()

        if family is not None:
            Fonts.family = family
            Fonts.global_font.configure(family=family)

        if size is not None:
            Fonts.size = size
            Fonts.global_font.configure(size=size)

        if weight is not None:
            Fonts.weight = weight
            Fonts.global_font.configure(weight=weight)

    @staticmethod
    def get_font(tipo: str|None) -> ctk.CTkFont:
        """Devuelve la fuente global para usar en widgets."""
        if Fonts.global_font is None:
            Fonts.init_fonts()
        if tipo:
            if tipo == "global_mini":
                return Fonts.global_font_mini
            elif tipo == "global_plus":
                return Fonts.global_font_plus
            elif tipo == "consolas":
                return Fonts.consolas
            elif tipo == "consolas_mini":
                return Fonts.consolas_mini
            else:
                return Fonts.global_font
        else:
            return Fonts.global_font
