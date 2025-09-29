import shutil

class FormatError():
    def __init__(self, message: str):
        self.message = "Error de formato :" + message

class Table():
    def __init__(self, columns:int, rows:int, name:str):
        self.columns = columns
        self.rows = rows
        self.name = name
        self.encabezados = []
        self.filas = []
        self.columns, self.rows = shutil.get_terminal_size()
    
    def add_encabezado(self, encabezado):
        if type(encabezado) == str:
            self.encabezados.append(encabezado)
        elif type(encabezado) == list:
            self.encabezados = encabezado
        else:
            raise FormatError("Como encabezados se reciben cadenas de caracteres o listas")

    def add_fila(self, filas: list = []):
        if len(filas) != len(self.encabezados):
            raise FormatError("los campos proporcionados superan el número de columnas de la tabla")
        self.filas.append(filas)

    def add_filas(self, filas: list = []):
        for fila in filas:
            if len(fila) != len(self.encabezados):
                raise FormatError("los campos proporcionados superan el número de columnas de la tabla")
        for fila in filas:
            self.filas.append(fila)

    def __get_table_size(self):
        table = [0] * len(self.encabezados)
        for _ in range(len(self.encabezados)):
            table[_] = len(self.encabezados[_])

        for _ in range(len(self.filas)):
            for idx in range(len(self.filas[_])):
                if len(self.filas[_][idx]) > table[idx]:
                    table[idx] = len(self.filas[_][idx])
        return table

    def __print_table_name(self, size):
        message1 = '+' + '-' * size + '+'
        longitud_nombre = len(self.name)
        size_differ = size-longitud_nombre
        indent = size_differ // 2
        message2 = '|' + " " * indent + self.name + " " * (indent if size_differ % 2 == 0 else indent + 1) + '|'
        print(message1.center(self.columns))
        print(message2.center(self.columns))
        print(message1.center(self.columns))
    
    def __print_header(self, size):
        iter = 0
        final = ""
        for header in self.encabezados:
            size_difer = size[iter] - len(header)
            indent = size_difer // 2
            mensaje = '|' + ' ' * indent + header + ' ' * (indent if size_difer % 2 == 0 else indent + 1)
            final += mensaje
            iter += 1
        final = final[:-1]
        print((final + '|').center(self.columns))
    
    def __print_separador(self, size):
        mensaje = ""
        for _ in size:
            mensaje += ('+' + '-' * _)
        mensaje = mensaje[:-1]
        mensaje += '+'
        print(mensaje.center(self.columns))
    
    def __print_rows(self, size:list):
        for fila in self.filas:
            iter = 0
            final = ""
            for val in fila:
                size_difer = size[iter] - len(val)
                indent = size_difer // 2
                mensaje = '|' + ' ' * indent + val + ' ' * (indent if size_difer % 2 == 0 else indent + 1)
                final += mensaje
                iter += 1
            final = final[:-1]
            print((final + '|').center(self.columns))



    def print_table(self):
        size_nonindent = self.__get_table_size()
        size = [n + 2 for n in size_nonindent]
        self.__print_table_name(sum(size))
        self.__print_header(size)
        self.__print_separador(size)
        self.__print_rows(size)
        self.__print_separador(size)


    def show_encabezados(self):
        print(self.encabezados)