"""
Linker - Verificación y análisis de archivos reubicables (.bin + .map)
"""

import os
import re
from dataclasses import dataclass
from typing import List, Tuple

import src.user_interface.logging.logger as logger

from .map_lexer import MapLexer

logger_handler = logger.configurar_logger()


@dataclass
class ProgramWord:
    """Palabra del binario, con información de reubicación"""

    kind: str  # absolute | reloc32 | reloc64
    value: int | None = None
    prefix: int | None = None
    placeholder: int | None = None


@dataclass
class MapEntry:
    """Entrada del mapa de memoria"""

    index: int
    address: int
    flag: int  # 1 ejecutable, 0 datos


class Linker:
    """Enlazador para validar y analizar programas reubicables"""

    _ABS_PATTERN = re.compile(r"^[01]{64}$")
    _RELOC32_PATTERN = re.compile(r"^([01]{32})\{(\d+)\}$")
    _RELOC64_PATTERN = re.compile(r"^\{(\d+)\}$")

    @staticmethod
    def verificar_bin(path: str) -> bool:
        """Verifica que un archivo .bin sea válido"""
        Linker._parse_bin(path)
        logger_handler.info(f"Archivo .bin válido: {path}")
        return True

    @staticmethod
    def verificar_map(path: str) -> bool:
        """Verifica que un archivo .map sea válido"""
        Linker._parse_map(path)
        logger_handler.info(f"Archivo .map válido: {path}")
        return True

    @staticmethod
    def verificar_programa(bin_path: str, map_path: str) -> bool:
        """Verifica que ambos archivos sean válidos"""
        Linker.analizar_programa(bin_path, map_path)
        return True

    @staticmethod
    def analizar_programa(
        bin_path: str, map_path: str
    ) -> Tuple[List[ProgramWord], List[MapEntry]]:
        """Obtiene la representación parseada de bin y map, validada"""
        program_words = Linker._parse_bin(bin_path)
        map_entries = Linker._parse_map(map_path)
        Linker._validate(program_words, map_entries)
        return program_words, map_entries

    # --- Internos ---

    @staticmethod
    def _parse_bin(path: str) -> List[ProgramWord]:
        if not os.path.exists(path):
            logger_handler.error(f"Archivo .bin no existe: {path}")
            raise FileNotFoundError(f"No existe el archivo {path}")

        words: List[ProgramWord] = []

        with open(path, "r", encoding="utf-8") as f:
            for lineno, raw in enumerate(f, 1):
                line = raw.strip()
                if line == "":
                    continue

                if match := Linker._ABS_PATTERN.fullmatch(line):
                    words.append(
                        ProgramWord(kind="absolute", value=int(match.group(0), 2))
                    )
                    continue

                if match := Linker._RELOC32_PATTERN.fullmatch(line):
                    prefix_bits, placeholder = match.groups()
                    words.append(
                        ProgramWord(
                            kind="reloc32",
                            prefix=int(prefix_bits, 2),
                            placeholder=int(placeholder),
                        )
                    )
                    continue

                if match := Linker._RELOC64_PATTERN.fullmatch(line):
                    placeholder = int(match.group(1))
                    words.append(ProgramWord(kind="reloc64", placeholder=placeholder))
                    continue

                logger_handler.error(
                    f"Formato inválido en {path} línea {lineno}: '{line}'"
                )
                raise ValueError(f"Formato inválido en {path} línea {lineno}: '{line}'")

        if not words:
            raise ValueError(f"Archivo .bin vacío: {path}")

        return words

    @staticmethod
    def _parse_map(path: str) -> List[MapEntry]:
        if not os.path.exists(path):
            logger_handler.error(f"Archivo .map no existe: {path}")
            raise FileNotFoundError(f"No existe el archivo {path}")

        lexer = MapLexer().build()
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        lexer.input(content)

        entries: List[MapEntry] = []
        current: List[int] = []

        for token in lexer:
            if token.type in ("NUMBER", "HEX"):
                current.append(token.value)
            elif token.type == "NEWLINE":
                if len(current) == 3:
                    entry_dict = {
                        "index": current[0],
                        "address": current[1],
                        "flag": current[2],
                    }
                    Linker._append_map_entry(entries, entry_dict, path)
                elif len(current) > 0:
                    logger_handler.warning(f"Línea incompleta ignorada: {current}")
                current = []

        if len(current) == 3:
            entry_dict = {
                "index": current[0],
                "address": current[1],
                "flag": current[2],
            }
            Linker._append_map_entry(entries, entry_dict, path)

        if not entries:
            raise ValueError(f"Archivo .map vacío: {path}")

        return entries

    @staticmethod
    def _append_map_entry(
        entries: List[MapEntry], data: dict[str, int], path: str
    ) -> None:
        required = {"index", "address", "flag"}
        if not required.issubset(data):
            missing = required - data.keys()
            raise ValueError(
                f"Entrada incompleta en {path}: faltan {', '.join(sorted(missing))}"
            )

        entries.append(
            MapEntry(index=data["index"], address=data["address"], flag=data["flag"])
        )

    @staticmethod
    def _validate(
        program_words: List[ProgramWord], map_entries: List[MapEntry]
    ) -> None:
        if len(program_words) != len(map_entries):
            raise ValueError(
                "El número de palabras del .bin no coincide con el mapa de memoria"
            )

        indices = {entry.index for entry in map_entries}
        expected = set(range(len(map_entries)))
        if indices != expected:
            raise ValueError(
                "El mapa de memoria no contiene todos los índices esperados"
            )

        max_placeholder = -1
        for word in program_words:
            if word.placeholder is not None:
                max_placeholder = max(max_placeholder, word.placeholder)

        if max_placeholder >= len(map_entries):
            raise ValueError(
                "Se encontró un marcador de reubicación fuera del rango del programa"
            )
