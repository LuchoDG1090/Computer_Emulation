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
from src.user_interface.cli.table_formater import Table
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
# Image helpers (non-destructive peek)
# -----------------------------

def _peek_img_range(path: str) -> tuple[int, int]:
    """Parse a .img file and return (min_addr, max_addr) without writing memory.
    Follows the same addressing rules as Loader.leer_img.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el documento {path}")
    dir_sig = None
    min_dir = None
    max_dir = None
    with open(path, 'r', encoding='utf-8') as f:
        for linea_no, instruccion in enumerate(f, 1):
            linea = instruccion.split('#', 1)[0].strip()
            if linea == '':
                continue
            if ':' in linea:
                izq, der = linea.split(':', 1)
                izq = izq.strip()
                der = der.strip()
                if izq == '':
                    if dir_sig is None:
                        raise ValueError(f"No se brindó una dirección para la instrucción en la linea {linea_no}")
                    dir = dir_sig
                else:
                    dir = int(izq, 0)
                    dir_sig = dir
                words = [w.strip() for w in der.split(',') if w.strip() != '']
            else:
                if dir_sig is None:
                    raise ValueError(f"No se brindó una dirección explicita para la instrucción en la linea {linea_no}")
                dir = dir_sig
                words = [w.strip() for w in linea.split(',') if w.strip() != '']
            for _ in words:
                if min_dir is None or dir < min_dir:
                    min_dir = dir
                if max_dir is None or dir > max_dir:
                    max_dir = dir
                dir += 8
                dir_sig = dir
    return (min_dir if min_dir is not None else 0, max_dir if max_dir is not None else -1)

def _peek_img_word_addrs(path: str) -> set[int]:
    """Parse a .img file and return the set of word-aligned addresses it would occupy."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el documento {path}")
    dir_sig = None
    occupied: set[int] = set()
    with open(path, 'r', encoding='utf-8') as f:
        for linea_no, instruccion in enumerate(f, 1):
            linea = instruccion.split('#', 1)[0].strip()
            if linea == '':
                continue
            if ':' in linea:
                izq, der = linea.split(':', 1)
                izq = izq.strip()
                der = der.strip()
                if izq == '':
                    if dir_sig is None:
                        raise ValueError(f"No se brindó una dirección para la instrucción en la linea {linea_no}")
                    dir = dir_sig
                else:
                    dir = int(izq, 0)
                    dir_sig = dir
                words = [w.strip() for w in der.split(',') if w.strip() != '']
            else:
                if dir_sig is None:
                    raise ValueError(f"No se brindó una dirección explicita para la instrucción en la linea {linea_no}")
                dir = dir_sig
                words = [w.strip() for w in linea.split(',') if w.strip() != '']
            for _ in words:
                occupied.add(dir)
                dir += 8
                dir_sig = dir
    return occupied


# -----------------------------
# Parsing helpers
# -----------------------------

def _prompt_int(message: str, allow_cancel: bool = True) -> Optional[int]:
    """Solicita un entero en decimal o hex (0x..). Retorna None si se cancela."""
    while True:
        s = _prompt_until_non_empty(message, allow_cancel=allow_cancel)
        if s is None:
            return None
        try:
            return int(s, 0)
        except ValueError:
            print(color.Color.ROJO)
            print("Valor inválido. Use decimal o hex (ej. 0x1000) o 'back' para volver.")
            print(color.Color.RESET_COLOR)


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
    # Registrar palabras ocupadas por este img
    try:
        # Reparse to get exact word addresses written (avoids changing loader)
        for addr in _peek_img_word_addrs(path):
            cpu.occupied_words.add(addr)
    except Exception:
        pass
    # Registrar segmento cargado para detectar colisiones y hacer core dumps útiles
    try:
        prog_name = os.path.basename(path)
        cpu.segments.append((min_addr or 0, (max_addr or 0) + 7, prog_name))
        cpu.current_program = path
    except Exception:
        pass
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
    # Auto-guardar el exec_map cargado (si hay direcciones)
    try:
        if getattr(cpu, 'exec_map', None) and len(cpu.exec_map) > 0:
            with open(exec_path, 'w', encoding='utf-8') as f:
                for a in sorted(cpu.exec_map):
                    f.write(hex(a) + "\n")
    except Exception:
        pass
    return min_addr, max_addr


def run_image(img_path: str, start_addr: int | None = None, step: bool = False):
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
    try:
        if step and hasattr(cpu, "run"):
            cpu.run_cycles()
        elif hasattr(cpu, "run"):
            cpu.run()
    except RuntimeError as e:
        # Segmentation fault / core dump
        print(color.Color.ROJO)
        print(f"ERROR: {e}")
        print("Generando core dump...")
        print(color.Color.RESET_COLOR)
        try:
            binp, txtp = cpu.dump_core()
            print(f"Core dump: {binp} | {txtp}")
        except Exception:
            pass
    print("Fin de ejecución")


# -----------------------------
# UI helpers
# -----------------------------

def _prompt_until_non_empty(message: str, allow_cancel: bool = False) -> Optional[str]:
    """Prompt until the user enters a non-empty value; returns None if canceled."""
    while True:
        try:
            print("back para regresar")
            val = input(message).strip()
            if val == "back":
                return None if allow_cancel else "back"
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
        else:
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

def _prompt_yes_no(message: str, default: Optional[bool] = None, allow_cancel: bool = True) -> Optional[bool]:
    """Prompt for yes/no. Returns True/False, or None if canceled.
    - Accepts: s/si/y/yes for yes, n/no for no.
    - If input is empty and default is not None, returns default.
    - If allow_cancel and user types back/menu/cancel/0, returns None.
    """
    while True:
        try:
            val = input(message).strip()
        except KeyboardInterrupt:
            logger_handler.exception("Interrupción del usuario durante prompt sí/no")
            print(color.Color.ROJO)
            print("Entrada equivocada")
            print(color.Color.RESET_COLOR)
            continue
        except EOFError:
            logger_handler.exception("EOF durante prompt sí/no")
            print(color.Color.ROJO)
            print("Entrada equivocada")
            print(color.Color.RESET_COLOR)
            continue
        if allow_cancel and val.lower() in ("back", "menu", "cancel", "0"):
            return None
        if val == "" and default is not None:
            return default
        v = val.lower()
        if v in ("s", "si", "y", "yes"):
            return True
        if v in ("n", "no"):
            return False
        print("Responda 's'/'n' o presione Enter para el valor por defecto.")

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

    # Editor de memoria interactivo
    sub.add_parser("mem", help="Editor de memoria interactivo (leer/escribir/exec y ejecutar)")

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
    if args.cmd == "mem":
        run_memory_editor()
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
        elif choice == '5':
            print("Ejecución por steps")
            logger_handler.info("Ejecución de archivo .img por pasos")    
            img_in = _prompt_existing_file("Ruta del archivo .img (sin o con extensión) (o 'back' para volver): ", ".img", allow_cancel=True)
            if img_in is None:
                continue
            start_s = input("PC inicial (hex como 0x4E20 o 'auto') (o 'back' para volver) [auto]: ").strip() or "auto"
            if start_s.lower() in ("back", "menu", "cancel", "0"):
                continue
            start = None if start_s.lower() == "auto" else int(start_s, 0)
            run_image(_normalize_output_img(img_in), start, True)
        elif choice == "6":
            run_memory_editor()
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


# -----------------------------
# Memory editor
# -----------------------------

def run_memory_editor():
    """Editor interactivo de memoria: leer/escribir bits/bytes/palabras, gestionar exec_map y ejecutar."""
    logger_handler.info("Editor de memoria iniciado")
    cpu = CPU(memory_size=65536)
    # Inicializar mapa de ejecución si no existe
    if not hasattr(cpu, 'exec_map') or cpu.exec_map is None:
        cpu.exec_map = set()

    # Construye menú con el mismo formato de la CLI principal
    msg = messages.Messages()
    mem_menu = Table(
        msg.columns,
        msg.rows,
        "Editor de memoria"
    )
    mem_menu.add_encabezado(["Opción", "Acción"])
    mem_menu.add_filas([
        ["1", "Cargar imagen (.img/.exec)"],
        ["2", "Ver memoria"],
        ["3", "Escribir memoria"],
        ["4", "Exec map"],
        ["5", "CPU (PC/Ejecutar)"],
        ["6", "Exportar/Importar"],
        ["9", "Volver"],
    ])

    # Submenús organizados
    def submenu_ver():
        view_menu = Table(messages.Messages().columns, messages.Messages().rows, "Memoria - Ver")
        view_menu.add_encabezado(["Opción", "Acción"])
        view_menu.add_filas([
            ["1", "Leer byte"],
            ["2", "Leer palabra 64-bit"],
            ["3", "Leer bit"],
            ["4", "Hexdump (rango)"],
            ["5", "Hexdump (memoria completa)"],
            ["9", "Volver"],
        ])

        def _hexdump(start: int, length: int, cols: int = 16):
            end = min(start + length, cpu.mem.size)
            data = cpu.mem.data[start:end]
            for off in range(0, len(data), cols):
                chunk = data[off:off+cols]
                hexs = ' '.join(f"{b:02X}" for b in chunk)
                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                print(f"{start+off:08X}: {hexs:<{cols*3}}  |{ascii_part}|")

        while True:
            print(color.Color.CYAN)
            view_menu.print_table()
            print(color.Color.RESET_COLOR)
            sub = (input("ver>> ").strip())
            if sub in ("9", "back", "menu"):
                break
            if sub == "1":
                addr = _prompt_int("Dirección (byte): ")
                if addr is None:
                    continue
                try:
                    v = cpu.mem.read_byte(addr)
                    print(f"BYTE[{addr}] = {v} (0x{v:02X})")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "2":
                addr = _prompt_int("Dirección base (byte): ")
                if addr is None:
                    continue
                try:
                    v = cpu.mem.read_word(addr)
                    print(f"WORD[{addr}] = {v} (0x{v:016X})")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "3":
                addr = _prompt_int("Dirección (byte): ")
                if addr is None:
                    continue
                bit = _prompt_int("Índice de bit [0-7]: ")
                if bit is None:
                    continue
                try:
                    v = cpu.mem.read_bit(addr, bit)
                    print(f"BIT[{addr}][{bit}] = {v}")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "4":
                start = _prompt_int("Inicio (byte): ")
                if start is None:
                    continue
                length = _prompt_int("Longitud (bytes): ")
                if length is None:
                    continue
                try:
                    cpu.mem._check_addr(start, max(0, length))
                    _hexdump(start, length)
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "5":
                resp = (_prompt_until_non_empty("Esto imprimirá mucha información. ¿Continuar? [s/N]: ", allow_cancel=True) or "n").lower()
                if resp.startswith('s'):
                    _hexdump(0, cpu.mem.size)
            else:
                print("Opción inválida")

    def submenu_escribir():
        write_menu = Table(messages.Messages().columns, messages.Messages().rows, "Memoria - Escribir")
        write_menu.add_encabezado(["Opción", "Acción"])
        write_menu.add_filas([
            ["1", "Escribir bit"],
            ["2", "Escribir byte"],
            ["3", "Escribir palabra 64-bit"],
            ["4", "Pegar hex"],
            ["5", "Rellenar (byte)"],
            ["6", "Rellenar (palabra 64-bit)"],
            ["7", "Cargar desde archivo"],
            ["9", "Volver"],
        ])
        while True:
            print(color.Color.CYAN)
            write_menu.print_table()
            print(color.Color.RESET_COLOR)
            sub = (input("escribir>> ").strip())
            if sub in ("9", "back", "menu"):
                break
            if sub == "1":
                addr = _prompt_int("Dirección (byte) [dec/hex]: ")
                if addr is None:
                    continue
                bit = _prompt_int("Índice de bit [0-7]: ")
                if bit is None:
                    continue
                val = _prompt_int("Valor (0 o 1): ")
                if val is None:
                    continue
                try:
                    if bit < 0 or bit > 7 or val not in (0,1):
                        raise ValueError("Bit debe estar entre 0-7 y valor 0/1")
                    cpu.mem.write_bit(addr, bit, val)
                    print("OK: bit escrito")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "2":
                addr = _prompt_int("Dirección (byte) [dec/hex]: ")
                if addr is None:
                    continue
                val = _prompt_int("Valor byte [0-255]: ")
                if val is None:
                    continue
                try:
                    cpu.mem.write_byte(addr, val)
                    print("OK: byte escrito")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "3":
                addr = _prompt_int("Dirección base (byte) [dec/hex]: ")
                if addr is None:
                    continue
                val = _prompt_int("Valor 64-bit [dec/hex]: ")
                if val is None:
                    continue
                try:
                    cpu.mem.write_word(addr, val)
                    print("OK: palabra 64-bit escrita (little-endian)")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "4":
                base = _prompt_int("Dirección base (byte): ")
                if base is None:
                    continue
                hx = _prompt_until_non_empty("Hex (ej. DE AD BE EF o deadbeef): ", allow_cancel=True)
                if hx is None:
                    continue
                norm = hx.replace(' ', '').replace('_', '')
                norm = norm.replace('0x', '').replace('0X', '')
                if len(norm) % 2 != 0:
                    print("Hex inválido: longitud impar")
                    continue
                try:
                    data = bytes.fromhex(norm)
                    cpu.mem._check_addr(base, len(data))
                    cpu.mem.data[base:base+len(data)] = data
                    print(f"OK: {len(data)} bytes escritos en 0x{base:X}")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "5":
                start = _prompt_int("Inicio (byte): ")
                if start is None:
                    continue
                length = _prompt_int("Longitud (bytes): ")
                if length is None:
                    continue
                val = _prompt_int("Valor byte [0-255]: ")
                if val is None:
                    continue
                try:
                    val_b = bytes([val & 0xFF])
                    cpu.mem._check_addr(start, max(0, length))
                    cpu.mem.data[start:start+length] = val_b * length
                    print("OK: rango rellenado")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "6":
                start = _prompt_int("Inicio (byte, alineado a 8): ")
                if start is None:
                    continue
                count = _prompt_int("Cantidad de palabras 64-bit: ")
                if count is None:
                    continue
                word_val = _prompt_int("Valor 64-bit [dec/hex]: ")
                if word_val is None:
                    continue
                try:
                    nbytes = max(0, count) * 8
                    cpu.mem._check_addr(start, nbytes)
                    pattern = (word_val & 0xFFFFFFFFFFFFFFFF).to_bytes(8, 'little')
                    cpu.mem.data[start:start+nbytes] = pattern * max(0, count)
                    print("OK: rango rellenado con palabras")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "7":
                base = _prompt_int("Dirección base (byte): ")
                if base is None:
                    continue
                path = _prompt_until_non_empty("Ruta del archivo origen: ", allow_cancel=True)
                if path is None or not os.path.exists(path):
                    print("Ruta inválida")
                    continue
                try:
                    with open(path, 'rb') as f:
                        data = f.read()
                    cpu.mem._check_addr(base, len(data))
                    cpu.mem.data[base:base+len(data)] = data
                    print(f"OK: {len(data)} bytes escritos en 0x{base:X}")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            else:
                print("Opción inválida")

    def submenu_exec():
        exec_menu = Table(messages.Messages().columns, messages.Messages().rows, "Exec map")
        exec_menu.add_encabezado(["Opción", "Acción"])
        exec_menu.add_filas([
            ["1", "Añadir dirección"],
            ["2", "Añadir rango"],
            ["3", "Limpiar"],
            ["4", "Mostrar"],
            ["9", "Volver"],
        ])
        while True:
            print(color.Color.CYAN)
            exec_menu.print_table()
            print(color.Color.RESET_COLOR)
            sub = (input("exec>> ").strip())
            if sub in ("9", "back", "menu"):
                break
            if sub == "1":
                addr = _prompt_int("Dirección ejecutable: ")
                if addr is None:
                    continue
                cpu.exec_map.add(addr)
                print("OK: dirección añadida a exec_map")
            elif sub == "2":
                start = _prompt_int("Inicio del rango: ")
                if start is None:
                    continue
                fin = _prompt_int("Fin del rango (inclusive): ")
                if fin is None:
                    continue
                if fin < start:
                    print("Rango inválido")
                else:
                    for a in range(start, fin+1, 8):
                        cpu.exec_map.add(a)
                    print("OK: rango añadido a exec_map (paso 8)")
            elif sub == "3":
                cpu.exec_map.clear()
                print("OK: exec_map limpiado")
            elif sub == "4":
                preview = sorted(list(cpu.exec_map))[:50]
                print(f"Exec count: {len(cpu.exec_map)}  |  Preview: {preview}")
            else:
                print("Opción inválida")

    def submenu_cpu():
        cpu_menu = Table(messages.Messages().columns, messages.Messages().rows, "CPU")
        cpu_menu.add_encabezado(["Opción", "Acción"])
        cpu_menu.add_filas([
            ["1", "Establecer PC"],
            ["2", "Ejecutar (run)"],
            ["3", "Ejecutar N ciclos (step)"],
            ["9", "Volver"],
        ])
        while True:
            print(color.Color.CYAN)
            cpu_menu.print_table()
            print(color.Color.RESET_COLOR)
            sub = (input("cpu>> ").strip())
            if sub in ("9", "back", "menu"):
                break
            if sub == "1":
                addr = _prompt_int("Nuevo PC: ")
                if addr is None:
                    continue
                cpu.pc = addr
                print(f"OK: PC = {cpu.pc}")
            elif sub == "2":
                print("Ejecutando...")
                try:
                    if hasattr(cpu, "run"):
                        cpu.run()
                    else:
                        for _ in range(1000000):
                            cpu.step()
                            if getattr(cpu, "halted", False):
                                break
                    print("Fin de ejecución")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error en ejecución: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "3":
                n = _prompt_int("Número de ciclos a ejecutar: ")
                if n is None:
                    continue
                try:
                    if hasattr(cpu, "run_cycles"):
                        cpu.run_cycles(n)
                    else:
                        for _ in range(max(0, n)):
                            cpu.step()
                            if getattr(cpu, "halted", False):
                                break
                    print("Step completado")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error en step: {e}")
                    print(color.Color.RESET_COLOR)
            else:
                print("Opción inválida")

    def submenu_export():
        exp_menu = Table(messages.Messages().columns, messages.Messages().rows, "Exportar/Importar")
        exp_menu.add_encabezado(["Opción", "Acción"])
        exp_menu.add_filas([
            ["1", "Volcar rango (.bin)"],
            ["2", "Volcar memoria completa (.bin)"],
            ["3", "Guardar exec_map (.exec)"],
            ["4", "Cargar exec_map (.exec)"],
            ["5", "Cargar exec asociado al .img"],
            ["9", "Volver"],
        ])
        while True:
            print(color.Color.CYAN)
            exp_menu.print_table()
            print(color.Color.RESET_COLOR)
            sub = (input("export>> ").strip())
            if sub in ("9", "back", "menu"):
                break
            if sub == "1":
                start = _prompt_int("Inicio (byte): ")
                if start is None:
                    continue
                length = _prompt_int("Longitud (bytes): ")
                if length is None:
                    continue
                out_path = _prompt_until_non_empty("Ruta de salida (.bin): ", allow_cancel=True)
                if out_path is None:
                    continue
                try:
                    cpu.mem._check_addr(start, max(0, length))
                    with open(out_path, 'wb') as f:
                        f.write(cpu.mem.data[start:start+length])
                    print("OK: rango volcado")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "2":
                out_path = _prompt_until_non_empty("Ruta de salida (.bin): ", allow_cancel=True)
                if out_path is None:
                    continue
                try:
                    with open(out_path, 'wb') as f:
                        f.write(cpu.mem.data)
                    print("OK: memoria completa volcada")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "3":
                out_path = _prompt_until_non_empty("Ruta de salida (.exec): ", allow_cancel=True)
                if out_path is None:
                    continue
                try:
                    with open(out_path, 'w', encoding='utf-8') as f:
                        for a in sorted(cpu.exec_map):
                            f.write(hex(a) + "\n")
                    print("OK: exec_map guardado")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "4":
                in_path = _prompt_until_non_empty("Ruta del archivo (.exec): ", allow_cancel=True)
                if in_path is None or not os.path.exists(in_path):
                    print("Ruta inválida")
                    continue
                try:
                    newmap = set()
                    with open(in_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            newmap.add(int(line, 0))
                    cpu.exec_map = newmap
                    print(f"OK: exec_map cargado ({len(newmap)} direcciones)")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            elif sub == "5":
                # Cargar el .exec asociado al último .img cargado
                if not getattr(cpu, 'current_program', None):
                    print("No hay imagen actual. Primero cargue un .img.")
                    continue
                assoc = cpu.current_program + ".exec"
                if not os.path.exists(assoc):
                    print(f"No se encontró: {assoc}")
                    continue
                try:
                    newmap = set()
                    with open(assoc, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            newmap.add(int(line, 0))
                    cpu.exec_map = newmap
                    print(f"OK: exec_map asociado cargado ({len(newmap)} direcciones)")
                except Exception as e:
                    print(color.Color.ROJO)
                    print(f"Error: {e}")
                    print(color.Color.RESET_COLOR)
            else:
                print("Opción inválida")

    while True:
        # Menú principal del editor (color diferenciado)
        print(color.Color.GREEN)
        mem_menu.print_table()
        print(color.Color.RESET_COLOR)
        cmd = (input("mem>> ").strip().lower() or "").strip()
        if cmd in ("9", "back", "menu", "exit", "salir"):
            logger_handler.info("Editor de memoria finalizado")
            break
        elif cmd == "1":
            # Cargar imagen y exec_map
            img = _prompt_existing_file("Ruta del archivo .img (o 'back' para volver): ", ".img", allow_cancel=True)
            if img is None:
                continue
            exec_present = os.path.exists(img + ".exec")
            try:
                # Validar imagen y calcular rango SIN escribir memoria
                Linker.revisar_img(img)
                # Precise occupied word addresses for the new image
                new_words = _peek_img_word_addrs(img)
                # Check precise collision with previously occupied words
                conflict_words = new_words.intersection(getattr(cpu, 'occupied_words', set()))
                has_collision = len(conflict_words) > 0
                if has_collision:
                    # Show a compact preview of collisions
                    preview = sorted(list(conflict_words))[:5]
                    print(color.Color.ROJO)
                    if cpu.segments:
                        # Report against first overlapping segment for context
                        print("Colisión de segmentos detectada (direcciones de palabra ya ocupadas)")
                    print(f"Ejemplos de colisión en: {[f'0x{a:08X}' for a in preview]} (total {len(conflict_words)})")
                    print("Sugerencia: cargue en una dirección diferente o cambie el .img")
                    print(color.Color.RESET_COLOR)
                if has_collision:
                    resp = _prompt_yes_no("Colisión detectada. ¿Cargar de todos modos? [s/N]: ", default=False, allow_cancel=True)
                    if resp is not True:
                        continue
                # Cargar (destructivo) y registrar segmento
                min_a, max_a = load_img(cpu, img)
                if not exec_present:
                    # Si no hay .exec asociado, limpiar para evitar residuos
                    cpu.exec_map = set()
                print(f"Imagen cargada en memoria: rango [{min_a}, {max_a}]")
                if exec_present:
                    print(f"Exec map cargado: {len(cpu.exec_map)} direcciones")
                    resp = _prompt_yes_no("¿Establecer PC al primer ejecutable? [s/N]: ", default=False, allow_cancel=True)
                    if resp is True:
                        cpu.pc = min(cpu.exec_map)
                        print(f"PC = 0x{cpu.pc:X}")
                else:
                    print("No se encontró archivo .exec. Puede definir exec_map con la opción 5.")
            except Exception as e:
                print(color.Color.ROJO)
                print(f"Error al cargar imagen: {e}")
                print(color.Color.RESET_COLOR)
        elif cmd == "2":
            submenu_ver()
        elif cmd == "3":
            submenu_escribir()
        elif cmd == "4":
            submenu_exec()
        elif cmd == "5":
            submenu_cpu()
        elif cmd == "6":
            submenu_export()
        else:
            print("Opción inválida")