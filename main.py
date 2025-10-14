#!/usr/bin/env python3
"""
Script principal para el emulador de CPU.

Este archivo sólo expone la función main() y delega la lógica de CLI al
módulo src/cli_runner.py.
"""

from src.user_interface.cli import cli_runner
from src.user_interface.gui import main as gui_runner

def main():
    """Punto de entrada de la aplicación (CLI)."""
    # cli_runner.run_cli()
    gui_runner.main_entry_point_gui()

if __name__ == "__main__":
    main()