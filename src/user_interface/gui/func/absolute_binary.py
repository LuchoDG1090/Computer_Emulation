"""
Módulo utilitario para manejar binarios absolutos.

Formato de archivo propuesto (texto plano, estable y fácil de depurar):

  - Primera línea opcional de cabecera:  "ABS64 V1"
  - Línea opcional de punto de entrada:  "START 0xHHHHHHHH" (dirección en bytes)
  - Registros de memoria (una por línea):
                0xHHHHHHHH 0bBBBB... (64 bits)
         o   0xHHHHHHHH 0xVVVVVVVVVVVVVVVV (16 dígitos hex, 64 bits)

  - Se permiten líneas en blanco y comentarios iniciados con '#'.
  - Las direcciones están en BYTES y deben ser múltiplos de 8 (palabra de 64 bits).
  - Solo se listan las celdas que deben escribirse. Las ausentes se dejan intactas
        (la RAM típica empieza en cero tras reset, por lo que equivalen a "vacías").

Compatibilidad con el formato anterior:
  - Si el archivo NO contiene direcciones y cada línea es un binario de 64 bits, se
        asume carga secuencial desde la dirección 0, avanzando de a 8 bytes por línea.

Este módulo se usa desde la GUI para cargar binarios absolutos en RAM, y también
puede ser reutilizado por CLIs o tests.

Todo el contenido y comentarios están en español por requerimiento explícito.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from src.memory.linker import MapEntry, ProgramWord  # Solo para usar las dataclasses


@dataclass
class AbsoluteEntry:
    """Par dirección-valor a escribir en memoria (dirección en bytes)."""

    address: int  # en bytes, múltiplo de 8
    value: int  # 64 bits


class AbsoluteParseError(Exception):
    pass


def _parse_int_token(tok: str) -> int:
    """Convierte un token numérico en int, aceptando '0x' (hex) o decimal.

    Levanta ValueError si el formato es inválido.
    """

    s = tok.strip().lower()
    if s.startswith("0x"):
        return int(s, 16)
    return int(s, 10)


def _parse_value_token(tok: str) -> int:
    """Convierte un valor a 64 bits.

    Acepta:
      - binario: 64 bits exactos (con o sin prefijo 0b, se ignoran espacios)
      - hexadecimal: 16 dígitos (con o sin 0x)
    """

    raw = tok.strip().replace(" ", "").lower()
    if set(raw) <= {"0", "1", "b", "x"}:
        # tratar como binario (permitir prefijo 0b)
        b = raw[2:] if raw.startswith("0b") else raw
        if not b or any(c not in "01" for c in b):
            raise ValueError("Valor binario inválido")
        if len(b) != 64:
            raise ValueError("Se esperan exactamente 64 bits")
        return int(b, 2)

    # tratar como hex (permitir prefijo 0x)
    h = raw[2:] if raw.startswith("0x") else raw
    if len(h) != 16 or any(c not in "0123456789abcdef" for c in h):
        raise ValueError("Valor hexadecimal de 64 bits inválido (16 dígitos)")
    return int(h, 16)


def parse_absolute_file(
    path: str, addresses_are_words: bool = False
) -> Tuple[List[AbsoluteEntry], Optional[int]]:
    """Parsea un archivo de binario absoluto.

    Retorna:
      - lista de AbsoluteEntry (address,value)
      - start_pc (opcional). Si no se especifica, se puede usar el mínimo address.

    Puede lanzar AbsoluteParseError ante formatos inválidos.
    """

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [ln.rstrip("\n") for ln in f]
    except OSError as e:
        raise AbsoluteParseError(f"No se pudo abrir el archivo: {e}")

    entries: List[AbsoluteEntry] = []
    start_pc: Optional[int] = None

    # Detectar si es el formato nuevo (con direcciones) o el simple (solo 64b)
    has_address_lines = False

    # Primera pasada: detectar cabecera/start y si hay direcciones
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        up = s.upper()
        if up.startswith("ABS64"):
            # cabecera informativa
            continue
        if up.startswith("START"):
            try:
                _, addr_tok = s.split(None, 1)
                start_pc = _parse_int_token(addr_tok)
            except Exception:
                raise AbsoluteParseError(
                    f"Línea START inválida: '{raw}'. Formato: START 0xHHHHHHHH"
                )
            continue

        # Si la línea tiene al menos 2 columnas, asuma formato con dirección
        parts = s.split()
        if len(parts) >= 2:
            # dirección + valor
            has_address_lines = True
            break

    if has_address_lines:
        # Segunda pasada: parsear todas las entradas dirección-valor
        for raw in lines:
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            up = s.upper()
            if up.startswith("ABS64") or up.startswith("START"):
                continue
            parts = s.split()
            if len(parts) < 2:
                # permitir líneas sueltas/ruido
                continue
            try:
                addr = _parse_int_token(parts[0])
                if addresses_are_words:
                    addr = addr * 8
                val = _parse_value_token(parts[1])
            except Exception as e:
                raise AbsoluteParseError(f"Entrada inválida: '{raw}': {e}")

            if addr % 8 != 0:
                raise AbsoluteParseError(
                    f"Dirección no alineada a 64 bits: 0x{addr:08X}"
                )

            entries.append(AbsoluteEntry(addr, val & 0xFFFFFFFFFFFFFFFF))
    else:
        # Formato antiguo: cada línea es una palabra de 64 bits desde 0
        addr = 0
        for raw in lines:
            s = raw.strip().replace(" ", "")
            if not s or s.startswith("#"):
                continue
            if not set(s) <= {"0", "1"}:
                raise AbsoluteParseError(
                    f"Línea no válida (64 bits binarios esperados): '{raw}'"
                )
            if len(s) != 64:
                raise AbsoluteParseError(
                    f"Longitud incorrecta: se esperan 64 bits, got {len(s)} bits"
                )
            entries.append(AbsoluteEntry(addr, int(s, 2)))
            addr += 8

    if not entries:
        raise AbsoluteParseError("No se encontraron entradas de memoria válidas")

    return entries, start_pc


def load_absolute_into_memory(
    memory, entries: Iterable[AbsoluteEntry]
) -> Tuple[int, int]:
    """Escribe todas las entradas en la memoria.

    Retorna (min_addr, max_addr) de los datos escritos (en bytes).
    """

    min_addr: Optional[int] = None
    max_addr: Optional[int] = None

    for ent in entries:
        if ent.address < 0 or ent.address + 8 > memory.size:
            raise ValueError(
                f"Dirección fuera de rango: 0x{ent.address:08X} (mem {memory.size} bytes)"
            )
        memory.write_word(ent.address, ent.value & 0xFFFFFFFFFFFFFFFF)
        min_addr = ent.address if min_addr is None else min(min_addr, ent.address)
        max_addr = ent.address if max_addr is None else max(max_addr, ent.address)

    if min_addr is None or max_addr is None:
        return 0, 0
    return min_addr, max_addr


def read_abs_bin_to_program_words(bin_path: str) -> List[ProgramWord]:
    """Lee un archivo .abs.bin (líneas de 64 bits) y devuelve ProgramWord absolutos.

    No usa el enlazador; solo parsea el binario absoluto.
    """

    words: List[ProgramWord] = []
    with open(bin_path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            s = raw.strip().replace(" ", "")
            if not s:
                continue
            if set(s) - {"0", "1"}:
                raise ValueError(
                    f"Línea inválida en {bin_path}:{lineno} (se esperaban 0/1): '{raw.strip()}'"
                )
            if len(s) != 64:
                raise ValueError(
                    f"Longitud inválida en {bin_path}:{lineno} (64 bits requeridos)"
                )
            val = int(s, 2)
            # ProgramWord(kind='absolute', value=val)
            words.append(ProgramWord(kind="absolute", value=val))

    if not words:
        raise ValueError(f"Archivo vacío: {bin_path}")
    return words


def read_abs_map_to_entries(map_path: str) -> List[MapEntry]:
    """Lee un archivo .abs.map con formato CSV: indice,direccion_decimal,flag

    Convención objetivo: direcciones en BYTES (decimal), como en el flujo reubicable.
    Tolerancia: si se detecta que el archivo trae posiciones en PALABRAS (p.ej. 2500)
    en lugar de bytes (20000), se aplica una corrección automática multiplicando x8.
    """

    raw_entries: List[tuple[int, int, int, int]] = []  # (lineno, idx, addr, flag)
    with open(map_path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            s = raw.strip()
            if not s:
                continue
            parts = [p.strip() for p in s.split(",")]
            if len(parts) != 3:
                raise ValueError(
                    f"Formato inválido en {map_path}:{lineno} -> '{raw.strip()}'"
                )
            try:
                idx = int(parts[0], 10)
                addr = int(parts[1], 10)
                flag = int(parts[2], 10)
            except Exception:
                raise ValueError(
                    f"Valores no numéricos en {map_path}:{lineno} -> '{raw.strip()}'"
                )
            if flag not in (0, 1):
                raise ValueError(f"Flag inválido en {map_path}:{lineno} -> {flag}")
            raw_entries.append((lineno, idx, addr, flag))

    if not raw_entries:
        raise ValueError(f"Archivo vacío: {map_path}")

    # Heurísticas de corrección para mapas "en palabras":
    # Caso A) Mapa 100% en palabras (addresses suben de 1 en 1): x8 directo.
    # Caso B) Mapa con bloque ejecutable con stride=8 pero base no alineada (p.ej. 2500, 2508, ...):
    #         queremos que el bloque empiece en 2500 palabras => 2500*8 bytes, y mantenga stride 8.
    #         Transformación: new_addr = (old_addr - base_old) * 8 + base_old * 8

    addrs = [addr for _, _, addr, _ in raw_entries]
    aligned_count = sum(1 for a in addrs if a % 8 == 0)

    by_index = sorted(raw_entries, key=lambda t: t[1])

    from collections import Counter

    # Deltas globales por índice (para detectar caso A)
    diffs_global = []
    prev = None
    for _, _, addr, _ in by_index:
        if prev is not None:
            diffs_global.append(addr - prev)
        prev = addr

    entries: List[MapEntry]

    # Caso A: stride común = 1 y ninguna alineada -> escalamos todo x8
    if aligned_count == 0 and diffs_global:
        cg, _ = Counter(diffs_global).most_common(1)[0]
        if cg == 1:
            print(
                f"Aviso: El mapa '{map_path}' parece estar en posiciones de palabra (stride=1). Se aplicará x8."
            )
            entries = [
                MapEntry(index=idx, address=addr * 8, flag=flag)
                for (_, idx, addr, flag) in raw_entries
            ]
            entries.sort(key=lambda e: e.index)
            return entries

    # Caso B: detectar bloque ejecutable con stride 8 pero base no alineada
    exec_by_index = [(idx, addr) for (_, idx, addr, flag) in by_index if flag == 1]
    if len(exec_by_index) >= 2:
        # Calcular diffs dentro del bloque ejecutable
        diffs_exec = []
        prev = None
        for _, addr in exec_by_index:
            if prev is not None:
                diffs_exec.append(addr - prev)
            prev = addr
        if diffs_exec:
            ce, _ = Counter(diffs_exec).most_common(1)[0]
            min_exec_addr = min(addr for _, addr in exec_by_index)
            if ce == 8 and (min_exec_addr % 8 != 0):
                base_old = min_exec_addr
                print(
                    f"Aviso: El bloque ejecutable del mapa '{map_path}' parece estar referido a posiciones de palabra desde {base_old}. Se re-escala a bytes alineados."
                )
                # Transformar SOLO los del bloque ejecutable, mantener el resto tal cual
                transformed = []
                for _, idx, addr, flag in raw_entries:
                    if flag == 1 and (addr - base_old) % 8 == 0:
                        # Queremos conservar stride de 8 bytes entre palabras y solo corregir la base:
                        # A_i = base_old + i*8  -->  B_i = base_old*8 + i*8  => new = addr - base_old + base_old*8
                        new_addr = (addr - base_old) + base_old * 8
                        transformed.append(
                            MapEntry(index=idx, address=new_addr, flag=flag)
                        )
                    else:
                        transformed.append(MapEntry(index=idx, address=addr, flag=flag))
                transformed.sort(key=lambda e: e.index)
                return transformed

    # Construcción por defecto (sin transformaciones de bloque)
    entries = [
        MapEntry(index=idx, address=addr, flag=flag)
        for _, idx, addr, flag in raw_entries
    ]

    # Paso final: asegurar alineación. Si alguna entrada quedó no alineada, interpretarla como posición de palabra
    # y convertir a bytes: addr *= 8
    fixed_any = False
    aligned_entries: List[MapEntry] = []
    for e in entries:
        if e.address % 8 != 0:
            aligned_entries.append(
                MapEntry(index=e.index, address=e.address * 8, flag=e.flag)
            )
            fixed_any = True
        else:
            aligned_entries.append(e)

    if fixed_any:
        print(
            f"Aviso: Se corrigieron direcciones no alineadas en '{map_path}' asumiendo posiciones de palabra (addr *= 8)."
        )

    aligned_entries.sort(key=lambda e: e.index)
    return aligned_entries
