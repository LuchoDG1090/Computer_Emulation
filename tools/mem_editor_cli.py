#!/usr/bin/env python3
import argparse
import sys
import os

# Importamos Memory desde src/memory/memory.py
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "memory"))
from memory import Memory


def main():
    parser = argparse.ArgumentParser(
        description="Memory Editor CLI - Herramienta para editar memoria bit a bit"
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- Comando: editar un bit ---
    edit_parser = subparsers.add_parser("edit", help="Editar un bit en memoria")
    edit_parser.add_argument("addr", type=lambda x: int(x, 0), help="Dirección (ej: 0x10 o 16)")
    edit_parser.add_argument("bit_index", type=int, help="Índice del bit (0-7)")
    edit_parser.add_argument("value", type=int, choices=[0, 1], help="Valor (0 o 1)")

    # --- Comando: leer memoria ---
    read_parser = subparsers.add_parser("read", help="Leer memoria")
    read_parser.add_argument("addr", type=lambda x: int(x, 0), help="Dirección (ej: 0x10 o 16)")
    read_parser.add_argument("--nbits", type=int, default=8, help="Número de bits (1,8,64)")

    # --- Comando: cargar archivo ---
    load_parser = subparsers.add_parser("load", help="Cargar memoria desde archivo")
    load_parser.add_argument("filename", help="Archivo binario o hex")

    # --- Comando: volcar archivo ---
    dump_parser = subparsers.add_parser("dump", help="Volcar memoria a archivo binario")
    dump_parser.add_argument("filename", help="Archivo destino")

    args = parser.parse_args()

    # Instanciamos memoria
    mem = Memory(size_words=16)  # 16 palabras de 64 bits = 128 bytes (ajustable)

    if args.command == "edit":
        mem.write_bit(args.addr, args.bit_index, args.value)
        print(f"[OK] Bit {args.bit_index} en addr {hex(args.addr)} -> {args.value}")

    elif args.command == "read":
        val = mem.bus_read(args.addr, args.nbits)
        print(f"[READ] Dirección {hex(args.addr)} ({args.nbits} bits): {val}")

    elif args.command == "load":
        if args.filename.endswith(".bin"):
            mem.load_from_binfile(args.filename)
            print(f"[OK] Memoria cargada desde binario {args.filename}")
        elif args.filename.endswith(".hex"):
            with open(args.filename, "r") as f:
                hex_data = f.read().strip().replace(" ", "")
                data = bytes.fromhex(hex_data)
                mem.memory[0:len(data)] = data
            print(f"[OK] Memoria cargada desde hex {args.filename}")
        else:
            print("[ERROR] Formato no soportado (usa .bin o .hex)")

    elif args.command == "dump":
        mem.dump_to_binfile(args.filename)
        print(f"[OK] Memoria volcada a {args.filename}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
