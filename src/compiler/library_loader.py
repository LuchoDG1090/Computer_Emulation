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
        Devuelve el código ASM de una función específica, con etiquetas internas renombradas.
        """
        if lib_path not in self.cache:
            self._parse_lib(lib_path)
        
        code = self.cache[lib_path].get(func_name, "")
        
        # Renombrar etiquetas internas (L1, L2, etc.) para evitar colisiones
        # Agregar prefijo basado en el nombre de la función
        import re
        
        # Encontrar todas las etiquetas internas (formato L seguido de números y opcionalmente _palabra)
        label_pattern = re.compile(r'\b(L\d+(?:_[a-zA-Z_][a-zA-Z0-9_]*)?)\b')
        
        # Crear un conjunto de etiquetas encontradas
        labels_found = set(label_pattern.findall(code))
        
        # Reemplazar cada etiqueta con versión prefijada
        for label in labels_found:
            # Crear nombre único: func_name + "_" + label
            prefixed_label = f"{func_name}_{label}"
            # Reemplazar todas las ocurrencias (tanto definiciones como referencias)
            code = re.sub(r'\b' + re.escape(label) + r'\b', prefixed_label, code)
        
        return code

    def _parse_lib(self, lib_path):
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Librería no encontrada: {lib_path}")

        functions = {}
        current_func = None
        current_code = []
        data_section = []  # Para almacenar sección de datos
        in_data_section = False

        with open(lib_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Regex para detectar etiquetas de función (SOLO al inicio de la línea, sin espacios antes)
        func_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*):')
        # Regex para detectar líneas de datos (var_X: DW, param_X: DW, etc.)
        data_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*):.*\b(DW|DB|RESW)\b')

        for line in lines:
            stripped = line.strip()
            
            # Manejo de líneas vacías y comentarios
            if not stripped or stripped.startswith('#') or stripped.startswith(';'):
                if current_func:
                    current_code.append(line)
                elif in_data_section:
                    data_section.append(line)
                continue

            # Verificar si es una línea de datos (DW, DB, RESW)
            data_match = data_pattern.match(line)
            if data_match:
                in_data_section = True
                data_section.append(line)
                continue

            # Verificar si es una definición de función (etiqueta sin indentación)
            # Usamos 'line' original para verificar que no tenga espacios al inicio
            match = func_pattern.match(line)
            
            if match:
                label = match.group(1)
                # Etiquetas especiales no son funciones
                if label in ('__MAIN', '__HEAP_PTR', '__HEAP_START'):
                    in_data_section = True
                    data_section.append(line)
                    continue
                
                # Solo considerar como función si empieza con FUNC_
                # Otras etiquetas (L1, L2, etc.) son labels internos
                if label.startswith('FUNC_'):
                    # Si ya estábamos leyendo una función, guardarla
                    if current_func:
                        functions[current_func] = "".join(current_code)
                    
                    # Iniciar nueva función
                    current_func = label
                    current_code = [line] # Incluir la etiqueta
                    in_data_section = False
                elif current_func:
                    # Es una etiqueta interna dentro de la función actual
                    current_code.append(line)
            else:
                # Es parte del cuerpo de la función actual (instrucción o etiqueta indentada)
                if current_func and not in_data_section:
                    current_code.append(line)
                elif in_data_section:
                    data_section.append(line)

        # Guardar la última función
        if current_func:
            functions[current_func] = "".join(current_code)

        # Agregar la sección de datos a todas las funciones que la necesiten
        if data_section:
            # Filtrar líneas especiales que no deben duplicarse (__HEAP_PTR, __HEAP_START, __MAIN, etc.)
            filtered_data = []
            for line in data_section:
                stripped = line.strip()
                # Excluir líneas con etiquetas especiales
                if any(label in stripped for label in ['__MAIN:', '__HEAP_PTR:', '__HEAP_START:', 'ORG ', 'JMP ', 'HALT']):
                    continue
                # Excluir líneas vacías o comentarios duplicados
                if not stripped or stripped.startswith('#') or stripped.startswith(';'):
                    continue
                filtered_data.append(line)
            
            if filtered_data:
                data_section_str = "".join(filtered_data)
                for func_name in functions:
                    # Solo agregar datos si la función los referencia
                    functions[func_name] = functions[func_name] + "\n" + data_section_str

        self.cache[lib_path] = functions
