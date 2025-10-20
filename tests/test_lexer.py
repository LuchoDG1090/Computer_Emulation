import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from src.assembler.lexer import lexer

# Test del lexer con identificadores
test_code = """
A_in_loop:
JNZ A_in_loop
MAT_A:
"""

lexer.input(test_code)

print("Tokens generados:")
for tok in lexer:
    print(f"  {tok.type:15} | {tok.value}")
