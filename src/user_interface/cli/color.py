class Color:
    RESET_COLOR  = '\033[0m' 
    ROJO   = '\033[31m\033[1A'
    AZUL   = '\033[34m\033[1A'
    YELLOW = '\033[33m\033[1A'
    GREEN  = '\033[32m\033[1A'
    CYAN   = '\033[36m\033[1A'
    PURPLE = '\033[35m\033[1A'
    CLEAR = '\033[2J'
    RESET_CURSOR = '\033[H'
    RESET_ALL = RESET_CURSOR + RESET_COLOR + CLEAR
