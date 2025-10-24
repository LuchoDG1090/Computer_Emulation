import hashlib
import os


class LoadedProgram:
    """Representa un programa cargado en memoria"""

    def __init__(self, name, min_addr, max_addr, entry_point, bin_path, map_path):
        self.name = name
        self.min_addr = min_addr
        self.max_addr = max_addr
        self.entry_point = entry_point
        self.bin_path = bin_path
        self.map_path = map_path


class CompilationRegistry:
    _registry = {}
    _loaded_programs = []
    _source_files = {}  # Mapea hash de código -> nombre de archivo original

    @classmethod
    def register(cls, source_code, bin_path, map_path, source_filename=None):
        code_hash = hashlib.md5(source_code.encode()).hexdigest()
        cls._registry[code_hash] = {
            "bin_path": bin_path,
            "map_path": map_path,
            "source": source_code,
        }
        if source_filename:
            cls._source_files[code_hash] = source_filename

    @classmethod
    def find_by_content(cls, source_code):
        code_hash = hashlib.md5(source_code.encode()).hexdigest()
        entry = cls._registry.get(code_hash)
        if entry:
            # Agregar el nombre del archivo fuente si existe
            entry["source_filename"] = cls._source_files.get(code_hash)
        return entry

    @classmethod
    def find_by_bin_name(cls, bin_filename):
        for entry in cls._registry.values():
            if os.path.basename(entry["bin_path"]) == bin_filename:
                return entry
        return None

    @classmethod
    def register_loaded_program(
        cls, name, min_addr, max_addr, entry_point, bin_path, map_path
    ):
        """Registra un programa que fue cargado en memoria"""
        program = LoadedProgram(
            name, min_addr, max_addr, entry_point, bin_path, map_path
        )
        cls._loaded_programs.append(program)
        return program

    @classmethod
    def get_loaded_programs(cls):
        """Obtiene lista de programas cargados en memoria"""
        return cls._loaded_programs

    @classmethod
    def clear_loaded_programs(cls):
        """Limpia la lista de programas cargados"""
        cls._loaded_programs = []
