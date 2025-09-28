#!/usr/bin/env python3
"""
Script principal para el emulador de CPU.

Este archivo sólo expone la función main() y delega la lógica de CLI al
módulo src/cli_runner.py.
"""

from src.cli_runner import run_cli


def main():
    """Punto de entrada de la aplicación (CLI)."""
    run_cli()

if __name__ == "__main__":
    main()