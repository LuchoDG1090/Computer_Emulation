"""
CLI runner utilities for assembling and running programs on the EUCLID-64 emulator.

This module provides a simple command-line interface and an interactive loop
to assemble .asm files into .img images, load them into the CPU via the
Linker/Loader, and run them with optional auto-start via the .exec map.
"""

import os
import argparse

from src.cpu.cpu import CPU
from src.assembler.assembler import Assembler
from src.loader.Linker_Loader import Linker, Loader


# -----------------------------
# Core actions
# -----------------------------

def assemble(input_path: str, output_path: str):
    """Assemble an .asm file into a .img image"""
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    Assembler().assemble(input_path, output_path)
    print(f"OK -> {output_path}")


def load_img(cpu: CPU, path: str):
    """Validate and load a .img image into CPU memory using the Loader.

    Returns (min_addr, max_addr) of written addresses and sets cpu.exec_map if
    a .exec sidecar file exists.
    """
    Linker.revisar_img(path)
    min_addr, max_addr = Loader.leer_img(cpu.mem, path)
    exec_path = path + ".exec"
    if os.path.exists(exec_path):
        exec_addrs = set()
        with open(exec_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                exec_addrs.add(int(line, 0))
        cpu.exec_map = exec_addrs
    return min_addr, max_addr


def run_image(img_path: str, start_addr: int | None = None):
    """Create a CPU, load the image, and run. Auto-start using .exec if present."""
    cpu = CPU(memory_size=65536)
    min_addr, _ = load_img(cpu, img_path)
    if start_addr is None:
        if getattr(cpu, 'exec_map', None):
            cpu.pc = min(cpu.exec_map)
        else:
            cpu.pc = min_addr or 0
    else:
        start = start_addr
        if getattr(cpu, 'exec_map', None) and start not in cpu.exec_map:
            try:
                start = min(a for a in cpu.exec_map if a >= start)
            except ValueError:
                start = min(cpu.exec_map)
        cpu.pc = start
    if hasattr(cpu, "run"):
        cpu.run()
    else:
        while True:
            cpu.step()
            if getattr(cpu, "halted", False):
                break
    print("Fin de ejecución")


# -----------------------------
# UI helpers
# -----------------------------

def print_menu():
    """Display the CLI menu for assembling/running user code"""
    print("\n" + "="*60)
    print("    EMULADOR DE CPU EUCLID-64 - INTERFAZ CLI")
    print("="*60)
    print("1) Ensamblar (.asm -> .img)")
    print("2) Ejecutar (.img)")
    print("3) Ensamblar y ejecutar")
    print("4) Información del formato de instrucciones")
    print("0) Salir")
    print("-"*60)


def _prompt_until_non_empty(message: str) -> str:
    """Prompt until the user enters a non-empty value."""
    while True:
        val = input(message).strip()
        if val:
            return val
        print("Por favor, ingrese una ruta válida.")


def _prompt_existing_file(message: str) -> str:
    """Prompt until the user enters a path to an existing file."""
    while True:
        path = _prompt_until_non_empty(message)
        if os.path.exists(path):
            return path
        print(f"No existe el archivo: {path}")


def show_format_info():
    """Print information about the instruction format."""
    print("\n" + "="*60)
    print("INFORMACION DEL FORMATO DE INSTRUCCIONES")
    print("="*60)
    print(
        "[63-56] Opcode (8 bits)\n"
        "[55-52] RD - Registro destino (4 bits)\n"
        "[51-48] RS1 - Registro fuente 1 (4 bits)\n"
        "[47-44] RS2 - Registro fuente 2 (4 bits)\n"
        "[43-32] FUNC - Campo de funcion o modificador (12 bits)\n"
        "[31-0]  IMM32 - Campo inmediato/direccion (32 bits)"
    )
    input("\nPresione Enter para continuar...")


# -----------------------------
# CLI parsing and dispatch
# -----------------------------

def parse_cli_args():
    parser = argparse.ArgumentParser(prog="main.py", description="Assembler/Runner CLI")
    sub = parser.add_subparsers(dest="cmd", required=False)

    p_asm = sub.add_parser("asm", help="Ensambla .asm a .img")
    p_asm.add_argument("-i", "--input", required=False)
    p_asm.add_argument("-o", "--output", required=False)

    p_run = sub.add_parser("run", help="Ejecuta una imagen .img")
    p_run.add_argument("-i", "--img", required=False)
    p_run.add_argument("--start", default="auto", help="PC inicial (ej. 0x4E20 o 'auto')")

    p_both = sub.add_parser("asmrun", help="Ensambla y ejecuta")
    p_both.add_argument("-i", "--input", required=False)
    p_both.add_argument("-o", "--output", required=False)
    p_both.add_argument("--start", default="auto")

    args, _ = parser.parse_known_args()
    return args


def handle_subcommands(args) -> bool:
    """Execute the given subcommand. Returns True if something was executed."""
    if args.cmd == "asm":
        in_path = args.input or _prompt_existing_file("Ruta del archivo .asm: ")
        out_path = args.output or _prompt_until_non_empty("Ruta de salida .img: ")
        assemble(in_path, out_path)
        return True
    if args.cmd == "run":
        img_in = args.img or _prompt_existing_file("Ruta del archivo .img: ")
        start = None if str(args.start).lower() == "auto" else int(args.start, 0)
        run_image(img_in, start)
        return True
    if args.cmd == "asmrun":
        in_path = args.input or _prompt_existing_file("Ruta del archivo .asm: ")
        out_path = args.output or _prompt_until_non_empty("Ruta de salida .img: ")
        assemble(in_path, out_path)
        start = None if str(args.start).lower() == "auto" else int(args.start, 0)
        run_image(out_path, start)
        return True
    return False


def run_cli():
    """Entry point for the application: subcommands or interactive loop."""
    args = parse_cli_args()
    if handle_subcommands(args):
        return

    # Interactive loop: run as many times as needed until exit
    while True:
        print_menu()
        choice = input("Seleccione una opción: ").strip()

        if choice == "0":
            break

        try:
            if choice == "1":
                asm_in = _prompt_existing_file("Ruta del archivo .asm: ")
                img_out = _prompt_until_non_empty("Ruta de salida .img: ")
                assemble(asm_in, img_out)
            elif choice == "2":
                img_in = _prompt_existing_file("Ruta del archivo .img: ")
                start_s = input("PC inicial (hex como 0x4E20 o 'auto') [auto]: ").strip() or "auto"
                start = None if start_s.lower() == "auto" else int(start_s, 0)
                run_image(img_in, start)
            elif choice == "3":
                asm_in = _prompt_existing_file("Ruta del archivo .asm: ")
                img_out = _prompt_until_non_empty("Ruta de salida .img: ")
                start_s = input("PC inicial (hex como 0x4E20 o 'auto') [auto]: ").strip() or "auto"
                assemble(asm_in, img_out)
                start = None if start_s.lower() == "auto" else int(start_s, 0)
                run_image(img_out, start)
            elif choice == "4":
                show_format_info()
            else:
                print("Opción no válida")
        except KeyboardInterrupt:
            print("\nInterrumpido por el usuario")
            break
        except Exception as e:
            print(f"Error: {e}")
