"""
Loader - Carga y reubicación de programas ensamblados
"""

import os
from typing import List, Tuple

import src.user_interface.logging.logger as logger

from .linker import Linker, MapEntry, ProgramWord

logger_handler = logger.configurar_logger()


class Loader:
    """Cargador que aplica las reubicaciones y carga en memoria"""

    WORD_SIZE = 8

    @staticmethod
    def cargar_bin(
        memory, program_words: List[ProgramWord], map_entries: List[MapEntry]
    ) -> Tuple[int, int]:
        """Escribe las palabras en sus direcciones absolutas según el mapa"""

        min_addr = None
        max_addr = None

        for entry, word in zip(map_entries, program_words):
            addr = entry.address

            # Verificar que la dirección esté en rango
            if addr + Loader.WORD_SIZE > memory.size:
                raise ValueError(f"Dirección 0x{addr:08X} fuera de rango de memoria")

            value = Loader._materializar_palabra(word, entry, map_entries)
            memory.write_word(addr, value)

            min_addr = addr if min_addr is None else min(min_addr, addr)
            max_addr = addr if max_addr is None else max(max_addr, addr)

        return (
            min_addr if min_addr is not None else 0,
            max_addr if max_addr is not None else 0,
        )

    @staticmethod
    def _materializar_palabra(
        word: ProgramWord, current_entry: MapEntry, all_entries: List[MapEntry]
    ) -> int:
        """Convierte una palabra con marcador en su valor absoluto"""
        if word.kind == "absolute":
            return word.value or 0

        if word.placeholder is None:
            raise ValueError("Palabra reubicable sin marcador de destino")

        # Buscar la dirección del placeholder en el mapa
        target_entry = next(
            (e for e in all_entries if e.index == word.placeholder), None
        )
        if target_entry is None:
            raise ValueError(f"Placeholder {word.placeholder} no encontrado en el mapa")

        target_addr = target_entry.address

        if word.kind == "reloc32":
            prefix = (word.prefix or 0) & 0xFFFFFFFF
            return (prefix << 32) | (target_addr & 0xFFFFFFFF)

        if word.kind == "reloc64":
            return target_addr & 0xFFFFFFFFFFFFFFFF

        raise ValueError(f"Tipo de palabra desconocido: {word.kind}")

    @staticmethod
    def cargar_programa(cpu, bin_path: str, map_path: str) -> None:
        """Carga un programa completo usando las direcciones absolutas del mapa"""

        program_words, map_entries = Linker.analizar_programa(bin_path, map_path)

        min_addr, max_addr = Loader.cargar_bin(cpu.mem, program_words, map_entries)

        # Obtener direcciones ejecutables directamente del mapa
        exec_addresses = {entry.address for entry in map_entries if entry.flag == 1}

        if cpu.exec_map is None:
            cpu.exec_map = set()

        cpu.exec_map.update(exec_addresses)

        cpu.pc = min(exec_addresses) if exec_addresses else 0
        cpu.segments.append((min_addr, max_addr, os.path.basename(bin_path)))
        cpu.current_program = bin_path

        logger_handler.info(
            f"Programa cargado: {bin_path}, PC=0x{cpu.pc:08X}, "
            f"segmento [0x{min_addr:08X}, 0x{max_addr:08X}]"
        )
