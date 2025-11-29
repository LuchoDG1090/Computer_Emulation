import os
import re

class LibraryLoader:
    def __init__(self):
        self.cache = {}

    def get_defined_functions(self, lib_path):
        """
        Analiza un archivo ASM y devuelve un conjunto de nombres de funciones (etiquetas).
        Asume que las funciones comienzan con 'Nombre:'
        """
        if lib_path in self.cache:
            return set(self.cache[lib_path].keys())

        self._parse_lib(lib_path)
        return set(self.cache[lib_path].keys())

    def get_function_code(self, lib_path, func_name):
        """
        Devuelve el código ASM de una función específica.
        """
        if lib_path not in self.cache:
            self._parse_lib(lib_path)
        
        return self.cache[lib_path].get(func_name, "")

    def _parse_lib(self, lib_path):
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Librería no encontrada: {lib_path}")

        functions = {}
        current_func = None
        current_code = []

        with open(lib_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Regex para detectar etiquetas de función (SOLO al inicio de la línea, sin espacios antes)
        func_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*):')

        for line in lines:
            stripped = line.strip()
            
            # Manejo de líneas vacías y comentarios
            if not stripped or stripped.startswith('#') or stripped.startswith(';'):
                if current_func:
                    current_code.append(line)
                continue

            # Verificar si es una definición de función (etiqueta sin indentación)
            # Usamos 'line' original para verificar que no tenga espacios al inicio
            match = func_pattern.match(line)
            
            if match:
                # Si ya estábamos leyendo una función, guardarla
                if current_func:
                    functions[current_func] = "".join(current_code)
                
                # Iniciar nueva función
                current_func = match.group(1)
                current_code = [line] # Incluir la etiqueta
            else:
                # Es parte del cuerpo de la función actual (instrucción o etiqueta indentada)
                if current_func:
                    current_code.append(line)

        # Guardar la última función
        if current_func:
            functions[current_func] = "".join(current_code)

        self.cache[lib_path] = functions
