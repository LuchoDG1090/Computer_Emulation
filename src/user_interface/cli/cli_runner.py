"""
CLI runner utilities for assembling and running programs on the EUCLID-64 emulator.

This module provides a simple command-line interface and an interactive loop
to assemble .asm files into .img images, load them into the CPU via the
Linker/Loader, and run them with optional auto-start via the .exec map.
"""

import os
import argparse
import math
from typing import Optional

from src.cpu.cpu import CPU
from src.assembler.assembler import Assembler
from src.loader.Linker_Loader import Linker, Loader
from src.user_interface.cli import messages, help_module, color
import src.user_interface.logging.logger as logger

logger_handler = logger.configurar_logger()

# -----------------------------
# Path helpers (extensions)
# -----------------------------

def _ensure_ext(path: str, expected_ext: str) -> str:
    """Append expected_ext if path has no extension."""
    root, ext = os.path.splitext(path)
    logger_handler.info(f"Asegurandose que el archivo {path} sea de extensión {expected_ext}")
    return path if ext else (path + expected_ext)

def _normalize_input_asm(path: str) -> str:
    return _ensure_ext(path, ".asm")

def _normalize_output_img(path: str) -> str:
    return _ensure_ext(path, ".img")


# -----------------------------
# Core actions
# -----------------------------

def assemble(input_path: str, output_path: str):
    """Assemble an .asm file into a .img image"""
    logger_handler.info(f"Proceso de ensamblado de {input_path} hacia {output_path}")
    input_path = _normalize_input_asm(input_path)
    output_path = _normalize_output_img(output_path)
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
    logger_handler.info("validando y cargando la umagen a a memoria por medio del cargador")
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
    logger_handler.info("Ejecución de una imagen")
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

def _prompt_until_non_empty(message: str, allow_cancel: bool = False) -> Optional[str]:
    """Prompt until the user enters a non-empty value; returns None if canceled."""
    while True:
        try:
            val = input(message).strip()
        except KeyboardInterrupt:
            print(color.Color.ROJO)
            logger_handler.exception("Entrada dada por el usuario no es valida, surgimiento de una excepción")
            print("Entrada equivocada")
            print(color.Color.RESET_COLOR)
        except EOFError:
            print(color.Color.ROJO)
            logger_handler.exception("Entrada dada por el usuario no es valida, surgimiento de una excepción")
            print("Entrada equivocada")
            print(color.Color.RESET_COLOR)
        if allow_cancel and val.lower() in ("back", "menu", "cancel", "0"):
            return None
        if val:
            return val
        print("Por favor, ingrese una ruta válida.")

def _prompt_existing_file(message: str, expected_ext: str | None = None, allow_cancel: bool = False) -> Optional[str]:
    """Prompt until the user enters a path to an existing file; returns None if canceled."""
    while True:
        raw = _prompt_until_non_empty(message, allow_cancel=allow_cancel)
        if raw is None:
            return None
        path = _ensure_ext(raw, expected_ext) if expected_ext else raw
        if os.path.exists(path):
            return path
        print(f"No existe el archivo: {path}")

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
        in_raw = args.input or _prompt_existing_file("Ruta del archivo .asm (sin o con extensión) (o 'back' para volver): ", ".asm", allow_cancel=True)
        if in_raw is None:
            return False
        out_raw = args.output or _prompt_until_non_empty("Ruta de salida .img (sin o con extensión) (o 'back' para volver): ", allow_cancel=True)
        if out_raw is None:
            return False
        assemble(_normalize_input_asm(in_raw), _normalize_output_img(out_raw))
        return True
    if args.cmd == "run":
        img_raw = args.img or _prompt_existing_file("Ruta del archivo .img (sin o con extensión) (o 'back' para volver): ", ".img", allow_cancel=True)
        if img_raw is None:
            return False
        img_in = _normalize_output_img(img_raw)
        start_arg = str(args.start)
        if start_arg.lower() == "auto":
            start = None
        else:
            try:
                start = int(start_arg, 0)
            except Exception:
                start = None
        run_image(img_in, start)
        return True
    if args.cmd == "asmrun":
        in_raw = args.input or _prompt_existing_file("Ruta del archivo .asm (sin o con extensión) (o 'back' para volver): ", ".asm", allow_cancel=True)
        if in_raw is None:
            return False
        out_raw = args.output or _prompt_until_non_empty("Ruta de salida .img (sin o con extensión) (o 'back' para volver): ", allow_cancel=True)
        if out_raw is None:
            return False
        in_path = _normalize_input_asm(in_raw)
        out_path = _normalize_output_img(out_raw)
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
    menu = messages.Messages()
    menu.print_general_info()
    menu.create_menu()
    logger_handler.info("CLI iniciada")

    # Interactive loop: run as many times as needed until exit
    while True:
        menu.print_menu()
        try:
            choice = input(">>").strip()
        except KeyboardInterrupt:
            logger_handler.exception("El usuario intentó finalizar de forma abrupta y equivocada la consola")
            messages.Messages().print_exit_msg()
            continue
        except EOFError:
            logger_handler.exception("El usuario ingresó una entrada no valida")
            messages.Messages().print_exit_msg()
            continue

        if choice == "clear()":
            logger_handler.info("Borrado de la consola")
            print(color.Color.RESET_ALL)
        elif choice == "1":
            logger_handler.info("inicio de procedimiento de ensamblado")
            asm_in = _prompt_existing_file("Ruta del archivo .asm (sin o con extensión) (o 'back' para volver): ", ".asm", allow_cancel=True)
            if asm_in is None:
                continue
            img_out = _prompt_until_non_empty("Ruta de salida .img (sin o con extensión) (o 'back' para volver): ", allow_cancel=True)
            if img_out is None:
                continue
            assemble(_normalize_input_asm(asm_in), _normalize_output_img(img_out))
        elif choice == "2":
            logger_handler.info("Ejecución de archivo .img")
            img_in = _prompt_existing_file("Ruta del archivo .img (sin o con extensión) (o 'back' para volver): ", ".img", allow_cancel=True)
            if img_in is None:
                continue
            start_s = input("PC inicial (hex como 0x4E20 o 'auto') (o 'back' para volver) [auto]: ").strip() or "auto"
            if start_s.lower() in ("back", "menu", "cancel", "0"):
                continue
            start = None if start_s.lower() == "auto" else int(start_s, 0)
            run_image(_normalize_output_img(img_in), start)
        elif choice == "3":
            logger_handler.info("Ensamblar y ejecutar")
            asm_in = _prompt_existing_file("Ruta del archivo .asm (sin o con extensión) (o 'back' para volver): ", ".asm", allow_cancel=True)
            if asm_in is None:
                continue
            img_out = _prompt_until_non_empty("Ruta de salida .img (sin o con extensión) (o 'back' para volver): ", allow_cancel=True)
            if img_out is None:
                continue
            start_s = input("PC inicial (hex como 0x4E20 o 'auto') (o 'back' para volver) [auto]: ").strip() or "auto"
            if start_s.lower() in ("back", "menu", "cancel", "0"):
                continue
            assemble(_normalize_input_asm(asm_in), _normalize_output_img(img_out))
            start = None if start_s.lower() == "auto" else int(start_s, 0)
            run_image(_normalize_output_img(img_out), start)
        elif choice == "4":
            logger_handler.info("Ingreso al módulo de ayuda")
            val = math.inf
            menu.create_help_menu()
            while val not in range(1,6):
                menu.print_help_menu()
                try:
                    raw = input(">>").strip().lower()
                    if raw in ("back", "menu", "cancel", "0"):
                        val = 5  # volver
                        break
                    val = int(raw)
                except ValueError:
                    logger_handler.exception("Valor ingresado equivocado")
                    print(color.Color.ROJO)
                    print("Entrada equivocada")
                    print(color.Color.RESET_COLOR)
                except EOFError:
                    logger_handler.exception("El usuario ingresó una entrada no valida")
                    print(color.Color.ROJO)
                    print("Entrada equivocada")
                    print(color.Color.RESET_COLOR)
                except KeyboardInterrupt:
                    logger_handler.exception("El usuario intentó finalizar de forma abrupta y equivocada la consola")
                    print(color.Color.ROJO)
                    print("Entrada equivocada")
                    print(color.Color.RESET_COLOR)
            if val == 1:
                help_module.Help().get_cli_help()
            elif val == 2:
                help_module.Help().get_machine_help()
            elif val == 3:
                help_module.Help().get_machine_help_verbose()
            elif val == 4:
                help_module.Help().formato_instrucciones()
            elif val == 5:
                pass
        elif choice == "exit()":
            logger_handler.info("CLI finalizada")
            print(color.Color.ROJO)
            print("Adios.")
            print(color.Color.RESET_COLOR)
            break
        else:
            logger_handler.error("CLI finalizada")
            print(color.Color.ROJO)
            print("Entrada equivocada")
            print(color.Color.RESET_COLOR)