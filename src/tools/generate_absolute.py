"""
Generador de binario absoluto a partir de código ensamblador.

Salida requerida:
- Archivo .bin: solo líneas con 64 bits ('0'/'1') por palabra (datos en BINARIO).
- Archivo .map: archivo separado con "indice,direccion_decimal,flag".
        (direccion en BYTES, en DECIMAL; flag=1 si ejecutable, 0 si dato).

Uso (CLI):
        python -m src.tools.generate_absolute -i input.asm -o output.abs.bin

Se generará también: output.abs.map junto al .bin indicado.
"""

from __future__ import annotations

import argparse
import os
import tempfile
from typing import List, Tuple

from src.assembler.assembler import Assembler
from src.memory.linker import Linker, MapEntry, ProgramWord
from src.memory.loader import Loader


def _materializar(
    program_words: List[ProgramWord], map_entries: List[MapEntry]
) -> List[Tuple[int, int]]:
    """Convierte palabras (con placeholders) a (address,value) absolutos.

    Retorna lista de tuplas (addr_en_bytes, valor_64bits)
    """

    out: List[Tuple[int, int]] = []
    for entry, word in zip(map_entries, program_words):
        val = Loader._materializar_palabra(word, entry, map_entries, offset=0)
        out.append((entry.address, val & 0xFFFFFFFFFFFFFFFF))
    return out


def generate_absolute(input_asm: str, output_bin: str) -> None:
    """Genera .abs.bin (binario puro) y .abs.map (decimal) a partir de un .asm"""

    asm = Assembler()
    # Generar bin y map temporales usando el ensamblador existente
    with tempfile.TemporaryDirectory() as tmp:
        bin_path = os.path.join(tmp, "tmp.bin")
        map_path = os.path.join(tmp, "tmp.map")

        asm.assemble_file(input_asm, bin_path, map_path)

        program_words, map_entries = Linker.analizar_programa(bin_path, map_path)

        # Corrección: Si el bloque ejecutable comienza en una dirección no alineada
        # (p.ej., 2500, 2508, 2516, ...), interpretamos que 2500 es la posición
        # de palabra deseada y reescalamos a bytes: new = (addr - base)*8 + base*8
        exec_entries = [e for e in map_entries if e.flag == 1]
        if len(exec_entries) >= 2:
            exec_sorted = sorted(exec_entries, key=lambda e: e.index)
            diffs = [
                exec_sorted[i].address - exec_sorted[i - 1].address
                for i in range(1, len(exec_sorted))
            ]
            from collections import Counter

            common = Counter(diffs).most_common(1)[0][0] if diffs else None
            min_exec = min(e.address for e in exec_entries)
            if common == 8 and (min_exec % 8 != 0):
                base = min_exec
                print(
                    f"[generate_absolute] Reescalando bloque ejecutable: base {base} -> {base * 8} (bytes)"
                )
                fixed = []
                for e in map_entries:
                    if e.flag == 1 and (e.address - base) % 8 == 0:
                        # Conservar stride de 8 bytes; corregir solo la base:
                        # A_i = base + i*8  -->  B_i = base*8 + i*8  => new = addr - base + base*8
                        new_addr = (e.address - base) + base * 8
                        fixed.append(
                            MapEntry(index=e.index, address=new_addr, flag=e.flag)
                        )
                    else:
                        fixed.append(e)
                map_entries = fixed

        # Paso final: asegurar alineación de todos los símbolos (exec y datos).
        # Si alguna dirección queda no alineada, interpretarla como posición de palabra -> bytes.
        aligned = []
        fixed_any = False
        for e in map_entries:
            if e.address % 8 != 0:
                aligned.append(
                    MapEntry(index=e.index, address=e.address * 8, flag=e.flag)
                )
                fixed_any = True
            else:
                aligned.append(e)
        if fixed_any:
            print("[generate_absolute] Corrigiendo direcciones no alineadas: addr *= 8")
        map_entries = aligned

    # Materializar todas las palabras a valores absolutos
    av = _materializar(program_words, map_entries)  # [(addr,val), ...]

    # Asegurar directorio de salida
    os.makedirs(os.path.dirname(output_bin) or ".", exist_ok=True)

    # .bin: solo 64 bits por línea, en orden de índice
    addr_to_val = {addr: val for addr, val in av}
    with open(output_bin, "w", encoding="utf-8") as fbin:
        for entry in sorted(map_entries, key=lambda e: e.index):
            val = addr_to_val.get(entry.address, 0)
            fbin.write(f"{val:064b}\n")

    # .map: indice,direccion_decimal,flag
    # CRITICO: las direcciones se emiten TAL CUAL en BYTES (decimal), igual que
    # en el flujo reubicable. NO se dividen por 8. El loader las usa directamente.
    map_out = os.path.splitext(output_bin)[0] + ".map"
    with open(map_out, "w", encoding="utf-8") as fmap:
        for entry in sorted(map_entries, key=lambda e: e.index):
            # entry.address ya está en BYTES (viene del ensamblador en bytes)
            fmap.write(f"{entry.index},{entry.address},{entry.flag}\n")

    print(f"✓ Generados: {output_bin} (binario) y {map_out} (mapa decimal)")


def main():
    parser = argparse.ArgumentParser(
        description="Genera un binario absoluto (ABS64 V1) desde un .asm"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Ruta al archivo .asm de entrada"
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        help="Ruta del .abs.bin de salida (por defecto junto al .asm)",
    )
    args = parser.parse_args()

    input_asm = args.input
    if not os.path.exists(input_asm):
        raise SystemExit(f"No existe el archivo de entrada: {input_asm}")

    if args.output:
        output_abs = args.output
    else:
        base, _ = os.path.splitext(input_asm)
        output_abs = base + ".abs.bin"

    generate_absolute(input_asm, output_abs)


if __name__ == "__main__":
    main()
