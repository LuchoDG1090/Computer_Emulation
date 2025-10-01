import shutil
from src.user_interface.cli.color import Color
from src.user_interface.cli.table_formater import Table

class Messages:
    def __init__(self):
        self.columns, self.rows = shutil.get_terminal_size()

        self.pc_name = """                                                                                      
                                                                                        dddddddd                                                     
EEEEEEEEEEEEEEEEEEEEEE                                      lllllll   iiii              d::::::d                         66666666         444444444  
E::::::::::::::::::::E                                      l:::::l  i::::i             d::::::d                        6::::::6         4::::::::4  
E::::::::::::::::::::E                                      l:::::l   iiii              d::::::d                       6::::::6         4:::::::::4  
EE::::::EEEEEEEEE::::E                                      l:::::l                     d:::::d                       6::::::6         4::::44::::4  
  E:::::E       EEEEEEuuuuuu    uuuuuu      cccccccccccccccc l::::l iiiiiii     ddddddddd:::::d                      6::::::6         4::::4 4::::4  
  E:::::E             u::::u    u::::u    cc:::::::::::::::c l::::l i:::::i   dd::::::::::::::d                     6::::::6         4::::4  4::::4  
  E::::::EEEEEEEEEE   u::::u    u::::u   c:::::::::::::::::c l::::l  i::::i  d::::::::::::::::d                    6::::::6         4::::4   4::::4  
  E:::::::::::::::E   u::::u    u::::u  c:::::::cccccc:::::c l::::l  i::::i d:::::::ddddd:::::d  ---------------  6::::::::66666   4::::444444::::444
  E:::::::::::::::E   u::::u    u::::u  c::::::c     ccccccc l::::l  i::::i d::::::d    d:::::d  -:::::::::::::- 6::::::::::::::66 4::::::::::::::::4
  E::::::EEEEEEEEEE   u::::u    u::::u  c:::::c              l::::l  i::::i d:::::d     d:::::d  --------------- 6::::::66666:::::64444444444:::::444
  E:::::E             u::::u    u::::u  c:::::c              l::::l  i::::i d:::::d     d:::::d                  6:::::6     6:::::6         4::::4  
  E:::::E       EEEEEEu:::::uuuu:::::u  c::::::c     ccccccc l::::l  i::::i d:::::d     d:::::d                  6:::::6     6:::::6         4::::4  
EE::::::EEEEEEEE:::::Eu:::::::::::::::uuc:::::::cccccc:::::cl::::::li::::::id::::::ddddd::::::dd                 6::::::66666::::::6         4::::4  
E::::::::::::::::::::E u:::::::::::::::u c:::::::::::::::::cl::::::li::::::i d:::::::::::::::::d                  66:::::::::::::66        44::::::44
E::::::::::::::::::::E  uu::::::::uu:::u  cc:::::::::::::::cl::::::li::::::i  d:::::::::ddd::::d                    66:::::::::66          4::::::::4
EEEEEEEEEEEEEEEEEEEEEE    uuuuuuuu  uuuu    cccccccccccccccclllllllliiiiiiii   ddddddddd   ddddd                      666666666            4444444444""".center(self.columns)

        self.lab_name =  """ 
+-+-+-+-+-+-+-+-+ +-+-+-+-+
|p|e|ñ|a|t|e|c|h| |l|a|b|s|
+-+-+-+-+-+-+-+-+ +-+-+-+-+
                        """.center(self.columns)
        
    @staticmethod
    def get_terminal_size():
        return shutil.get_terminal_size()
    
    def delete_scr(self):
        print(Color.RESET_ALL)

    def print_pc_name(self):
        print(Color.YELLOW)
        print(self.pc_name)
        print(Color.RESET_COLOR)

    def print_lab_name(self):
        print(Color.CYAN)
        print(self.lab_name)
        print(Color.RESET_COLOR)

    def print_general_info(self):
        self.delete_scr()
        self.print_pc_name()
        self.print_lab_name()

    def print_exit_msg(self):
        print(Color.ROJO)
        print("Para salir ingrese exit()".center(self.columns))
        print(Color.RESET_COLOR)

    def print_instruction_info(self):
        print(Color.PURPLE)
        print('#' * self.columns)
        self.print_exit_msg()
        print(Color.GREEN)
        print("Para limpiar ingrese clear()".center(self.columns))
        print(Color.CYAN)
        print("Para obtener ayuda ingrese help(), helpv(), helpcli(), helpins() o helpinsv()".center(self.columns))
        print("1) Ensamblar (.asm -> .img)".center(self.columns))
        print("2) Ejecutar (.img)".center(self.columns))
        print("3) Ensamblar y ejecutar".center(self.columns))
        print("4) Obtener ayuda".center(self.columns))
        print(Color.RESET_COLOR)
        print("Comience a ingresar las instrucciones en la linea de comandos".center(self.columns))
        print(Color.PURPLE)
        print('#' * self.columns)
        print(Color.RESET_COLOR)
    
    def create_help_menu(self):
        self.table = Table(self.columns,
                      self.rows,
                      "Opciones de ayuda")
        self.table.add_encabezado(["Opción", "Descripcion"])
        self.table.add_filas(
            [["1", "Ayuda con las instrucciones de la cli"],
             ["2", "Ayuda con las instrucciones de la maquina emulada"],
             ["3", "Ayuda descriptiva de las instrucciones de la maquina emulada"],
             ["4", "Ayuda con el formato de las instrucciones"],
             ["5", "regresar"]]
        )

    def print_help_menu(self):
        print(Color.PURPLE)
        self.table.print_table()
        print(Color.RESET_COLOR)
    
    def create_menu(self):
        self.menu_table = Table(
            self.columns,
            self.rows,
            "Menú de opciones"
        )
        self.menu_table.add_encabezado(
            ["Opción", "Instrucción"]
        )
        self.menu_table.add_filas(
            [["clear()", "Limpiar la terminal"],
            ["1", "Ensamblar (.asm -> .img)"],
            ["2", "Ejecutar (.img)"],
            ["3", "Ensamblar y ejecutar"],
            ["4", "Ayuda"],
            ["5", "Ejecutar (.img) instrucción por instrucción"],
            ["exit()", "Salir"]]
        )
    
    def print_menu(self):
        print(Color.AZUL)
        self.menu_table.print_table()
        print(Color.RESET_COLOR)