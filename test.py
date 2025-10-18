from src.assembler.assembler import Assembler

assembler = Assembler()

try:
    assembler.assemble_file(
        input_file="C:\\Users\\Bellic12\\Documents\\GitHub\\Computer_Emulation\\programs\\mcd_peña.asm",
        output_binary="C:\\Users\\Bellic12\\Documents\\GitHub\\Computer_Emulation\\build\\mcd_peña.bin",
        output_map="C:\\Users\\Bellic12\\Documents\\GitHub\\Computer_Emulation\\build\\mcd_peña.map",
    )
except Exception as e:
    print(f"Error: {e}")
