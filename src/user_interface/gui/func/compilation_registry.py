import hashlib
import os


class CompilationRegistry:
    _registry = {}

    @classmethod
    def register(cls, source_code, bin_path, map_path):
        code_hash = hashlib.md5(source_code.encode()).hexdigest()
        cls._registry[code_hash] = {
            "bin_path": bin_path,
            "map_path": map_path,
            "source": source_code,
        }

    @classmethod
    def find_by_content(cls, source_code):
        code_hash = hashlib.md5(source_code.encode()).hexdigest()
        return cls._registry.get(code_hash)

    @classmethod
    def find_by_bin_name(cls, bin_filename):
        for entry in cls._registry.values():
            if os.path.basename(entry["bin_path"]) == bin_filename:
                return entry
        return None
