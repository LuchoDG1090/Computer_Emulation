import customtkinter as ctk
from .design_variable_elements import Fonts
from src.cpu.isa import Opcodes

class ProgramCounterFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.cpu = kwargs.get("cpu", None)
        self.columnconfigure(0, weight=0) # Label "PC:"
        self.columnconfigure(1, weight=1) # Entry PC
        self.columnconfigure(2, weight=3) # Instruction Label
        self.rowconfigure(0, weight=1)

        self.__build_widgets()

    def __build_widgets(self):
        label = ctk.CTkLabel(
            self, text="PC:", font=Fonts.get_font("consolas"), text_color="white"
        )
        label.grid(row=0, column=0, sticky="e", padx=(5, 2))

        self.pc_entry = ctk.CTkEntry(
            self,
            font=Fonts.get_font("consolas"),
            text_color="#00FF00",
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#00FF00",
            width=60 # Reduced width
        )
        self.pc_entry.grid(row=0, column=1, sticky="ew", padx=2, pady=5)
        self.pc_entry.insert(0, "0")

        # Binding para actualizar PC al presionar Enter
        self.pc_entry.bind("<Return>", self.__on_pc_enter)
        
        # Label para mostrar la instrucción actual
        self.instruction_label = ctk.CTkLabel(
            self,
            text="NOP",
            font=Fonts.get_font("consolas"),
            text_color="#AAAAAA",
            fg_color="#1a1a1a",
            corner_radius=4,
            anchor="w",
            width=300  # Fixed width to prevent resizing
        )
        self.instruction_label.grid(row=0, column=2, sticky="ew", padx=(2, 5), pady=5)

    def __on_pc_enter(self, event=None):
        """Actualiza el PC del CPU cuando el usuario presiona Enter."""
        if not self.cpu:
            print("CPU no disponible")
            return

        try:
            pc_text = self.pc_entry.get().strip()
            if not pc_text:
                return

            # Aceptar decimal, hex (0x...) o binario (0b...)
            if pc_text.lower().startswith("0x"):
                new_pc = int(pc_text, 16)
            elif pc_text.lower().startswith("0b"):
                new_pc = int(pc_text, 2)
            else:
                # Interpretar como posición de palabra (word_position), convertir a byte address
                word_pos = int(pc_text, 10)
                new_pc = word_pos * 8

            # Validar rango
            if hasattr(self.cpu, "memory") and self.cpu.memory:
                max_addr = self.cpu.memory.size
            else:
                max_addr = 1024 * 1024  # Default 1MB

            if new_pc < 0 or new_pc >= max_addr:
                print(f"PC fuera de rango: {new_pc} (memoria: 0-{max_addr - 1})")
                # Restaurar valor anterior
                self.update_pc(self.cpu.pc)
                return

            # Setear PC
            self.cpu.pc = new_pc

            # Actualizar display
            self.update_pc(new_pc)

            word_position = new_pc // 8
            print(f"PC actualizado a: {new_pc} (palabra {word_position}, 0x{new_pc:X})")

        except ValueError as e:
            print(f"Valor inválido para PC: {e}")
            # Restaurar valor anterior si hay error
            if self.cpu:
                self.update_pc(self.cpu.pc)

    def update_pc(self, pc: int):
        """Actualiza el valor del Program Counter mostrando posición de palabra e instrucción"""
        word_position = pc // 8
        self.pc_entry.delete(0, "end")
        self.pc_entry.insert(0, str(word_position))
        
        # Actualizar instrucción mostrada
        if self.cpu:
            inst_text = self._get_instruction_text(pc)
            self.instruction_label.configure(text=f" {inst_text}")

    def _get_instruction_text(self, pc):
        """Decodifica la instrucción en PC para mostrarla"""
        try:
            if not hasattr(self.cpu, "mem") or not hasattr(self.cpu, "decoder"):
                return "---"
                
            # Verificar límites de memoria
            if pc < 0 or pc >= self.cpu.mem.size:
                return "OOB"

            instruction = self.cpu.mem.read_word(pc)
            decoded = self.cpu.decoder.decode(instruction)
            opcode_val = decoded["opcode"]
            
            try:
                opcode_name = Opcodes(opcode_val).name
            except ValueError:
                return f"UNK ({opcode_val:02X})"
            
            # Formateo simple
            parts = [opcode_name]
            
            rd = decoded["rd"]
            rs1 = decoded["rs1"]
            rs2 = decoded["rs2"]
            imm = decoded["imm32"]
            
            # Lógica de visualización básica
            if opcode_name in ["JMP", "CALL", "JZ", "JNZ", "JC", "JNC", "JS"]:
                 parts.append(f"0x{imm:X}")
            elif opcode_name in ["MOVI", "ADDI"]:
                 parts.append(f"R{rd}, #{imm}")
            elif opcode_name in ["LD", "ST"]:
                 parts.append(f"R{rd}, [R{rs1}+{imm}]")
            elif opcode_name in ["ADD", "SUB", "MUL", "DIV", "AND", "OR", "XOR", "CMP"]:
                 parts.append(f"R{rd}, R{rs1}, R{rs2}")
            elif opcode_name in ["NOT", "CP"]:
                 parts.append(f"R{rd}, R{rs1}")
            elif opcode_name in ["PUSH", "POP"]:
                 parts.append(f"R{rd}")
            elif opcode_name in ["IN", "OUT"]:
                 parts.append(f"R{rd}, Port {imm}")
            
            return " ".join(parts)
            
        except Exception as e:
            return "ERR"

