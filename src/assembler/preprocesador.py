
import os
import re
from .exceptions import PreprocessorError

class MacroTable:
    def __init__(self):
        self.macros = {}
    
    def add(self, name, value):
        if name in self.macros:
            raise PreprocessorError(f"Macro duplicada: {name}")
        self.macros[name] = value
    
    def get(self, name):
        return self.macros.get(name)
    
    def replace_in_line(self, line):
        words = line.split()
        result = []
        for word in words:
            clean_word = word.strip(',;:()[]')
            if clean_word in self.macros:
                result.append(word.replace(clean_word, self.macros[clean_word]))
            else:
                result.append(word)
        return ' '.join(result)

class Preprocessor:
    def __init__(self):
        self.macro_table = MacroTable()
        self.include_paths = ['.', 'includes']
        self.processed_files = set()
        
        # Patrones regex que plantee en el doc
        self.patterns = {
            'include_quoted': re.compile(r'^\s*#include\s+"([^"]+)"'),
            'include_system': re.compile(r'^\s*#include\s+<([^>]+)>'),
            'define': re.compile(r'^\s*#define\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(.*)')
        }
    
    def preprocess_file(self, filename):
        """Preprocesa un archivo completo"""
        self.processed_files.clear()
        return self._process_file(filename, os.path.dirname(filename))
    
    def _process_file(self, filename, base_dir):
        if filename in self.processed_files:
            raise PreprocessorError(f"Inclusión cíclica: {filename}")
        
        self.processed_files.add(filename)
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise PreprocessorError(f"Archivo no encontrado: {filename}")
        
        output_lines = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            try:
                processed_line = self._process_line(line, base_dir)
                if processed_line is not None:
                    output_lines.append(processed_line)
            except PreprocessorError as e:
                raise PreprocessorError(f"Línea {line_num}: {str(e)}")
        
        return '\n'.join(output_lines)
    
    def _process_line(self, line, base_dir):
        # Probar patrones de include
        match_quoted = self.patterns['include_quoted'].match(line)
        if match_quoted:
            included_file = match_quoted.group(1)
            return self._handle_include(included_file, base_dir, system_file=False)
        
        match_system = self.patterns['include_system'].match(line)
        if match_system:
            included_file = match_system.group(1)
            return self._handle_include(included_file, base_dir, system_file=True)
        
        # Probar patrón define
        match_define = self.patterns['define'].match(line)
        if match_define:
            macro_name = match_define.group(1)
            macro_value = match_define.group(2).strip()
            self.macro_table.add(macro_name, macro_value)
            return None
        
        # Línea normal - reemplazar macros
        return self.macro_table.replace_in_line(line)
    
    def _handle_include(self, filename, base_dir, system_file):
        if system_file:
            search_dirs = self.include_paths
        else:
            search_dirs = [base_dir] + self.include_paths
        
        for search_dir in search_dirs:
            potential_path = os.path.join(search_dir, filename)
            if os.path.exists(potential_path):
                return self._process_file(potential_path, os.path.dirname(potential_path))
        
        raise PreprocessorError(f"Archivo incluido no encontrado: {filename}")
    
    def clear_macros(self):
        self.macro_table.macros.clear()