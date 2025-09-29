import json
import shutil
from pathlib import Path
from src.user_interface.cli.color import Color
from src.user_interface.cli.table_formater import Table

class Help:
    def __init__(self, dir:str = r'\files\help.json', cli_dir: str = r'\files\cli_help.json'):
        """Método constructor para definir los parámetros necesarios para desplegar las ayudas de la cli

        Args:
            dir (str, optional): _description_. Defaults to r'\files\help.json'.
            cli_dir (str, optional): _description_. Defaults to r'\files\cli_help.json'.
            type (str, optional): _description_. Defaults to "both".
        """
        working_dir = str(Path.cwd())
        self.dir = working_dir + dir
        self.cli = working_dir + cli_dir
    
    def __get_file_content(self) -> dict:
        """Obtener los contenidos del archivo de ayuda para las instrucciones de la máquina

        Returns:
            dict: Estructura de datos con las instrucciones de la maquina que se está emulando
        """
        try:
            with open(self.dir, 'r', encoding = 'utf-8') as f:
                return json.load(f)
        except FileNotFoundError as e:
            print(Color.ROJO)
            print("Archivo no encontrado: " + str(e))
            print(Color.RESET_CURSOR)
    
    def __get_cli_help_file_content(self) -> dict:
        """Obtener los contenidos del archivo de ayuda para las instrucciones de la linea de comandos (CLI)

        Returns:
            dict: Estructura de datos con las instrucciones de la linea de comandos (command line interface)
        """
        try:
            with open(self.cli, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError as e:
            print(Color.ROJO)
            print("Archivo no encontrado: " + str(e))
            print(Color.RESET_CURSOR)

    def get_machine_help_verbose(self) -> None:
        """Imprimir en la consola toda la información de las instrucciones disponibles
        de la maquina
        """
        contents = self.__get_file_content()
        instrucciones = list(contents.keys())
        contador = 1
        for instruccion in instrucciones:
            print(str(contador) + '. ' + instruccion)
            print('\t' + '- Descripción: ' + contents[instruccion]['Info'])
            print('\t' + '- Sintaxis: ' + contents[instruccion]['Example'])
            print('\t' + '- Opcode: ' + contents[instruccion]['Opcode'])
            print('\t' + '- Sintaxis: ' + contents[instruccion]['Example'])
            print('\t' + '- Tipo: ' + contents[instruccion]['Type'])
            if contents[instruccion]['Params']:
                print('\t' + '- Parámetros: ')
                for param in contents[instruccion]['Params']:
                    print('\t\t' + '* ' +param)
            contador += 1

    def get_machine_help(self) -> None:
        """Imprimir en pantalla la información reducida de las instrucciones de la maquina
        """
        contents = self.__get_file_content()
        instrucciones = list(contents.keys())
        contador = 1
        for instruccion in instrucciones:
            print(f'{str(contador)}. {instruccion}: {contents[instruccion]['Info']}')
            contador += 1

    def get_cli_help(self) -> None:
        """Imprimir en consola la información de las instrucciones de la linea de comandos
        """
        contents = self.__get_cli_help_file_content()
        instrucciones = list(contents.keys())
        contador = 1
        for instruccion in instrucciones:
            print(f'{str(contador)}. {instruccion}: {contents[instruccion]['Info']}')
    
    def formato_instrucciones(self) -> None:
        "Imprimir en consola el formato de las instrucciones"
        columns, rows = shutil.get_terminal_size()
        tabla_formato = Table(
            columns,
            rows,
            "Formato de instrucciones"
        )
        tabla_formato.add_encabezado(["Formato", "Significado"])
        tabla_formato.add_filas(
            [
                ["[63-56]", "Opcode (8 bits)"],
                ["[55-52]", "RD - Registro destino (4 bits)"],
                ["[51-48]", "RS1 - Registro fuente 1 (4 bits)"],
                ["[47-44]", "RS2 - Registro fuente 2 (4 bits)"],
                ["[43-32]", "FUNC - Campo de funcion o modificador (12 bits)"],
                ["[31-0]", "IMM32 - Campo inmediato/direccion (32 bits)"]
            ]
        )
        tabla_formato.print_table()