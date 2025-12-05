"""
SimpleDisk - Disco virtual simple para almacenar programas ensamblador.

Este módulo implementa un disco virtual que almacena programas compilados
en formato ensamblador (.asm) en un archivo binario disk.img.

Estructura del disco:
- Header (4KB): Índice JSON con metadata de programas
- Data: Programas almacenados secuencialmente

"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict


class SimpleDisk:
    """
    Disco virtual simple para almacenar programas ensamblador.
    Similar a CommunicatingAgents pero para programas en lugar de agentes.
    """
    
    HEADER_SIZE = 4096  # 4KB para índice JSON
    
    def __init__(self, disk_path: str = "disk.img"):
        """
        Inicializa disco virtual.
        
        Args:
            disk_path: Ruta al archivo disk.img (default: "disk.img" en directorio actual)
        """
        self.path = disk_path
        self.programs: Dict[str, Dict] = {}
        self._init_disk()
    
    def _init_disk(self):
        """Inicializa disco si no existe, o carga índice existente"""
        if not os.path.exists(self.path):
            self._format_disk()
        else:
            self._load_index()
    
    def _format_disk(self):
        """Crea disco vacío con header JSON"""
        print(f"\033[33m[SimpleDisk] Formateando '{self.path}'...\033[0m")
        
        # Header vacío (4KB de JSON)
        header = json.dumps({}).encode('utf-8').ljust(self.HEADER_SIZE, b'\x00')
        
        with open(self.path, 'wb') as f:
            f.write(header)
        
        self.programs = {}
        print(f"\033[32m[SimpleDisk] Disco formateado: {self.HEADER_SIZE} bytes iniciales\033[0m")
    
    def _load_index(self):
        """Carga índice de programas desde el header del disco"""
        try:
            with open(self.path, 'rb') as f: # rb --> leer binario
                header_bytes = f.read(self.HEADER_SIZE)
                header_str = header_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
                
                if header_str:
                    self.programs = json.loads(header_str)
                else:
                    self.programs = {}
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"\033[31m[SimpleDisk] Error al cargar índice: {e}\033[0m")
            self.programs = {}
    
    def _save_index(self):
        """Guarda índice de programas en el header del disco"""
        header = json.dumps(self.programs, indent=2).encode('utf-8')
        
        if len(header) > self.HEADER_SIZE:
            raise ValueError(
                f"Índice muy grande ({len(header)} bytes, max {self.HEADER_SIZE}). "
                f"Reduce el número de programas o aumenta HEADER_SIZE."
            )
        
        header_padded = header.ljust(self.HEADER_SIZE, b'\x00')
        
        with open(self.path, 'r+b') as f:
            f.seek(0)
            f.write(header_padded)
    
    def write_program(self, name: str, asm_code: str) -> bool:
        """
        Escribe programa al disco.
        
        Args:
            name: Nombre del programa (sin extensión .asm)
            asm_code: Código ensamblador completo
        
        Returns:
            True si se escribió exitosamente
        
        Raises:
            ValueError: Si el nombre es muy largo (>50 caracteres)
        """
        if len(name) > 50:
            raise ValueError(f"Nombre muy largo: '{name}' (max 50 caracteres)")
        
        if name in self.programs:
            print(f"\033[33m[SimpleDisk] Programa '{name}' ya existe, sobrescribiendo...\033[0m")
        
        # Calcular offset (al final del archivo)
        if os.path.exists(self.path):
            current_size = os.path.getsize(self.path)
        else:
            current_size = self.HEADER_SIZE
        
        offset = current_size
        
        # Escribir código al final del disco
        code_bytes = asm_code.encode('utf-8')
        
        with open(self.path, 'ab') as f:
            f.write(code_bytes)
        
        # Actualizar índice
        self.programs[name] = {
            'offset': offset,
            'size': len(code_bytes),
            'timestamp': datetime.now().isoformat(),
            'lines': asm_code.count('\n') + 1
        }
        self._save_index()
        
        print(f"\033[32m[SimpleDisk] '{name}' escrito: {len(code_bytes)} bytes, {self.programs[name]['lines']} líneas\033[0m")
        return True
    
    def read_program(self, name: str) -> Optional[str]:
        """
        Lee programa desde disco.
        
        Args:
            name: Nombre del programa
        
        Returns:
            Código ensamblador o None si no existe
        """
        if name not in self.programs:
            return None
        
        prog_info = self.programs[name]
        offset = prog_info['offset']
        size = prog_info['size']
        
        with open(self.path, 'rb') as f:
            f.seek(offset)
            code_bytes = f.read(size)
        
        return code_bytes.decode('utf-8')
    
    def delete_program(self, name: str) -> bool:
        """
        Elimina programa del índice (no del disco físico para evitar fragmentación).
        
        Args:
            name: Nombre del programa
        
        Returns:
            True si se eliminó, False si no existía
        """
        if name not in self.programs:
            return False
        
        del self.programs[name]
        self._save_index()
        
        print(f"\033[31m[SimpleDisk] '{name}' eliminado del índice\033[0m")
        return True
    
    def list_programs(self) -> List[Dict[str, any]]:
        """
        Lista todos los programas almacenados.
        
        Returns:
            Lista de diccionarios con información de cada programa
        """
        programs_list = []
        
        for name, info in self.programs.items():
            programs_list.append({
                'name': name,
                'size': info['size'],
                'lines': info.get('lines', 0),
                'timestamp': info['timestamp']
            })
        
        return sorted(programs_list, key=lambda x: x['name'])
    
    def get_disk_info(self) -> str:
        """
        Retorna información del disco formateada.
        
        Returns:
            String con información del disco
        """
        if not os.path.exists(self.path):
            return "\033[35m[DiskInfo] Disco no inicializado\033[0m"
        
        total_size = os.path.getsize(self.path)
        num_programs = len(self.programs)
        used_space = sum(p['size'] for p in self.programs.values())
        
        return (
            f"\033[35m[DiskInfo] "
            f"Programs={num_programs} | "
            f"Total={total_size} bytes | "
            f"Used={used_space} bytes | "
            f"Free={total_size - used_space - self.HEADER_SIZE} bytes\033[0m"
        )
    
    def program_exists(self, name: str) -> bool:
        """
        Verifica si un programa existe en el disco.
        
        Args:
            name: Nombre del programa
        
        Returns:
            True si existe, False en caso contrario
        """
        return name in self.programs
    
    def get_program_info(self, name: str) -> Optional[Dict]:
        """
        Obtiene información de un programa específico.
        
        Args:
            name: Nombre del programa
        
        Returns:
            Diccionario con información o None si no existe
        """
        if name not in self.programs:
            return None
        
        info = self.programs[name].copy()
        info['name'] = name
        return info
    
    def compact_disk(self) -> int:
        """
        Compacta el disco eliminando espacio de programas borrados.
        
        Returns:
            Bytes liberados
        """
        if not self.programs:
            print("\033[33m[SimpleDisk] No hay programas para compactar\033[0m")
            return 0
        
        print("\033[33m[SimpleDisk] Compactando disco...\033[0m")
        
        # Leer todos los programas activos
        active_programs = {}
        for name in self.programs.keys():
            code = self.read_program(name)
            if code:
                active_programs[name] = code
        
        # Guardar tamaño original
        original_size = os.path.getsize(self.path)
        
        # Recrear disco
        self._format_disk()
        
        # Reescribir programas
        for name, code in active_programs.items():
            self.write_program(name, code)
        
        # Calcular espacio liberado
        new_size = os.path.getsize(self.path)
        freed = original_size - new_size
        
        print(f"\033[32m[SimpleDisk] Compactación completada: {freed} bytes liberados\033[0m")
        return freed
