import sys
import os

# Añadir directorios al path
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, 'src'))
sys.path.append(os.path.join(current_dir, 'examples'))
# ...existing code...

import argparse
import re
from assembler.assembler import Assembler
from cpu.cpu import CPU  # ajusta si tu ruta difiere
from loader.Linker_Loader import Linker, Loader

HEX = re.compile(r"^\s*0x([0-9A-Fa-f]+)\s*:\s*0x([0-9A-Fa-f]+)\s*$")

def assemble(input_path: str, output_path: str):
    dir_name = os.path.dirname(output_path)
    if dir_name:  # ✅ solo crear carpeta si hay ruta
        os.makedirs(dir_name, exist_ok=True)
    Assembler().assemble(input_path, output_path)
    print(f"OK -> {output_path}")


def load_img(cpu: CPU, path: str):
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
    cpu = CPU(memory_size=65536)
    min_addr, max_addr = load_img(cpu, img_path)
    # Auto-alinear PC si hay mapa de ejecutables
    if start_addr is None:
        if cpu.exec_map:
            cpu.pc = min(cpu.exec_map)
        else:
            cpu.pc = min_addr or 0
    else:
        start = start_addr
        if cpu.exec_map and start not in cpu.exec_map:
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

def main():
    parser = argparse.ArgumentParser(prog="test.py", description="Assembler/Runner CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_asm = sub.add_parser("asm", help="Ensambla .asm a .img")
    p_asm.add_argument("-i", "--input", default=os.path.join("programs", "mcd_peña.asm"))
    p_asm.add_argument("-o", "--output", default=os.path.join("build", "mcd_peña.img"))

    p_run = sub.add_parser("run", help="Ejecuta una imagen .img")
    p_run.add_argument("-i", "--img", default=os.path.join("build", "mcd_peña.img"))
    p_run.add_argument("--start", default="auto", help="PC inicial (ej. 0x4E20 o 'auto')")

    p_both = sub.add_parser("asmrun", help="Ensambla y ejecuta")
    p_both.add_argument("-i", "--input", default=os.path.join("programs", "mcd_peña.asm"))
    p_both.add_argument("-o", "--output", default=os.path.join("build", "mcd_peña.img"))
    p_both.add_argument("--start", default="auto")

    args = parser.parse_args()

    if args.cmd == "asm":
        assemble(args.input, args.output)
    elif args.cmd == "run":
        start = None if str(args.start).lower() == "auto" else int(args.start, 0)
        run_image(args.img, start)
    elif args.cmd == "asmrun":
        assemble(args.input, args.output)
        start = None if str(args.start).lower() == "auto" else int(args.start, 0)
        run_image(args.output, start)

if __name__ == "__main__":
    main()