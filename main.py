#!/usr/bin/env python3
"""
Script principal para ejecutar ejemplos del emulador de CPU

Este script permite ejecutar diferentes ejemplos y demostraciones
del emulador de CPU
"""

import os
import argparse

from src.cpu.cpu import CPU
from src.assembler.assembler import Assembler
from src.loader.Linker_Loader import Linker, Loader

# -----------------------------
# Utilidades CLI (asm/run)
# -----------------------------

def assemble(input_path: str, output_path: str):
    """Ensambla un archivo .asm en una imagen .img"""
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    Assembler().assemble(input_path, output_path)
    print(f"OK -> {output_path}")


def load_img(cpu: CPU, path: str):
    """Valida y carga una imagen .img en la memoria del CPU mediante el Loader.

    Devuelve (min_addr, max_addr) de las direcciones escritas y carga el mapa
    de direcciones ejecutables si existe el archivo .exec asociado.
    """
    # Validar formato .img
    Linker.revisar_img(path)
    # Cargar a memoria externa de la CPU (Memory)
    min_addr, max_addr = Loader.leer_img(cpu.mem, path)
    # Cargar mapa de ejecutables si existe
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
    """Crea un CPU, carga la imagen y ejecuta, con auto-inicio por .exec si aplica."""
    cpu = CPU(memory_size=65536)
    min_addr, max_addr = load_img(cpu, img_path)
    # Auto-alinear PC si hay mapa de ejecutables
    if start_addr is None:
        if getattr(cpu, 'exec_map', None):
            cpu.pc = min(cpu.exec_map)
        else:
            cpu.pc = min_addr or 0
    else:
        start = start_addr
        if getattr(cpu, 'exec_map', None) and start not in cpu.exec_map:
            # elegir la siguiente direccion ejecutable >= start; si no hay, usar la minima
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

def print_menu():
    """Muestra el menú de opciones para ensamblar/ejecutar código propio"""
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
    """Pide por consola hasta que el usuario ingrese una cadena no vacía."""
    while True:
        val = input(message).strip()
        if val:
            return val
        print("Por favor, ingrese una ruta válida.")


def _prompt_existing_file(message: str) -> str:
    """Pide una ruta a archivo existente hasta que sea válida."""
    while True:
        path = _prompt_until_non_empty(message)
        if os.path.exists(path):
            return path
        print(f"No existe el archivo: {path}")


def show_format_info():
    """Muestra informacion sobre el formato de instrucciones"""
    print("\n" + "="*60)
    print("INFORMACION DEL FORMATO DE INSTRUCCIONES")
    print("="*60)
    
    print("[63-56] Opcode (8 bits)\n[55-52] RD - Registro destino (4 bits)\n[51-48] RS1 - Registro fuente 1 (4 bits)\n[47-44] RS2 - Registro fuente 2 (4 bits)\n[43-32] FUNC - Campo de funcion o modificador (12 bits)\n[31-0]  IMM32 - Campo inmediato/direccion (32 bits)")
    
    input("\nPresione Enter para continuar...")

def main():
    """CLI principal estilo test.py con modo interactivo sencillo.

    Subcomandos disponibles:
      - asm: Ensambla un .asm a .img
      - run: Ejecuta una imagen .img
      - asmrun: Ensambla y ejecuta

    Si no se especifica subcomando, se ofrece un flujo interactivo para
    seleccionar acción, archivo de entrada y salida, y PC inicial opcional.
    """
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

    # Modo subcomando (no interactivo)
    if args.cmd == "asm":
        in_path = args.input or _prompt_existing_file("Ruta del archivo .asm: ")
        out_path = args.output or _prompt_until_non_empty("Ruta de salida .img: ")
        assemble(in_path, out_path)
        return
    if args.cmd == "run":
        img_in = args.img or _prompt_existing_file("Ruta del archivo .img: ")
        start = None if str(args.start).lower() == "auto" else int(args.start, 0)
        run_image(img_in, start)
        return
    if args.cmd == "asmrun":
        in_path = args.input or _prompt_existing_file("Ruta del archivo .asm: ")
        out_path = args.output or _prompt_until_non_empty("Ruta de salida .img: ")
        assemble(in_path, out_path)
        start = None if str(args.start).lower() == "auto" else int(args.start, 0)
        run_image(out_path, start)
        return

    # Modo interactivo sencillo
    print_menu()
    choice = input("Seleccione una opción: ").strip()

    if choice == "0":
        return

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
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()