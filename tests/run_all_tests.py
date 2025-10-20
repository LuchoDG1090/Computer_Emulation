"""
Script para ejecutar todos los tests del emulador
"""

import subprocess
import sys
from pathlib import Path

# Obtener directorio de tests
TESTS_DIR = Path(__file__).parent
PYTHON = sys.executable

# Tests a ejecutar (en orden)
TESTS = [
    ("Tests de Memoria", "test_memory.py"),
    ("Tests de CPU", "test_cpu.py"),
    ("Tests de Ensamblador", "test_assembler.py"),
    ("Ejecución Automática (MCD)", "test_execution_auto.py"),
]


def run_test(name, test_file):
    """Ejecuta un test y reporta resultado"""
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")

    test_path = TESTS_DIR / test_file

    try:
        result = subprocess.run(
            [PYTHON, str(test_path)],
            cwd=TESTS_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )

        print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode == 0:
            print(f"✅ {name} - PASADO")
            return True
        else:
            print(f"❌ {name} - FALLIDO (código {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️ {name} - TIMEOUT (más de 30s)")
        return False
    except Exception as e:
        print(f"❌ {name} - ERROR: {e}")
        return False


def main():
    """Ejecuta todos los tests"""
    print("=" * 60)
    print("  SUITE DE TESTS DEL EMULADOR DE CPU")
    print("=" * 60)

    results = []

    for name, test_file in TESTS:
        passed = run_test(name, test_file)
        results.append((name, passed))

    # Resumen
    print("\n" + "=" * 60)
    print("  RESUMEN DE TESTS")
    print("=" * 60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✅ PASADO" if passed else "❌ FALLADO"
        print(f"  {status:12} - {name}")

    print(f"\n  Total: {passed_count}/{total_count} tests pasados")

    if passed_count == total_count:
        print("\n  🎉 ¡TODOS LOS TESTS PASARON!")
        return 0
    else:
        print(f"\n  ⚠️  {total_count - passed_count} test(s) fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main())
