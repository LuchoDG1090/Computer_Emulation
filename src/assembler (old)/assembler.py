import src.assembler.encoder

class Assembler:
    def __init__(self):
        self.encoder = src.assembler.encoder.Encoder()
        self.word_size = 8            # tamaño de palabra (64 bits)
        self.loc = 0                  # contador de ubicación actual
        self.symbols = {}             # tabla de símbolos (etiqueta -> dirección)

    def assemble(self, asm_file, output_img):
        # PASADA 1: recolectar símbolos y nodos (dirección + tokens)
        self.loc = 0
        self.symbols.clear()
        nodes = []  # cada nodo: {'addr': int, 'tokens': list[str]}

        with open(asm_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(lines)

        for raw in lines:
            tokens = self.parse_line(raw)
            if not tokens:
                continue

            # etiqueta al inicio: "mcd:" o "loop:"
            if tokens[0].endswith(':'):
                label = tokens[0][:-1]
                if not label:
                    raise ValueError("Etiqueta vacía")
                if label in self.symbols:
                    raise ValueError(f"Etiqueta duplicada: {label}")
                self.symbols[label] = self.loc
                tokens = tokens[1:]  # resto de la línea tras la etiqueta
                if not tokens:
                    continue  # solo etiqueta en la línea

            head = tokens[0].upper()

            if head == 'ORG':
                if len(tokens) < 2:
                    raise ValueError("ORG requiere una dirección")
                self.loc = self._parse_int(tokens[1])
                continue

            if head == 'EXEC_FROM':
                # Guardar como nodo (no consume palabra)
                nodes.append({'addr': self.loc, 'tokens': tokens})
                continue

            # Manejo especial de DW/RESW para ajustar 'loc' por el tamaño real
            if head == 'DW':
                # cantidad de valores en esta línea (tokens después de 'DW')
                count_vals = max(0, len(tokens) - 1)
                nodes.append({'addr': self.loc, 'tokens': tokens})
                self.loc += self.word_size * count_vals
                continue

            if head == 'RESW':
                if len(tokens) != 2:
                    raise ValueError("RESW requiere un argumento (cantidad)")
                try:
                    count = self._parse_int(tokens[1])
                except Exception as e:
                    raise ValueError(f"RESW argumento inválido: {tokens[1]}") from e
                nodes.append({'addr': self.loc, 'tokens': tokens})
                self.loc += self.word_size * count
                continue

            # Instrucción normal: registra dirección actual y tokens
            nodes.append({'addr': self.loc, 'tokens': tokens})
            self.loc += self.word_size

        # PASADA 2: resolver símbolos y emitir palabras codificadas
        emitted = []
        exec_addrs: list[int] = []      # direcciones de instrucciones (8-byte aligned)
        exec_from_addr: int | None = None  # inicio de rango continuo (opcional)
        for n in nodes:
            resolved = self._resolve_tokens(n['tokens'])
            tokens = resolved
            mnemonic = tokens[0].upper()

            # --- Directiva EXEC_FROM (opcional) ---
            if mnemonic == "EXEC_FROM":
                if len(tokens) == 2:
                    exec_from_addr = self._parse_int(tokens[1])
                else:
                    exec_from_addr = n['addr']  # desde la posición actual
                continue

            # --- Directiva DW: emitir datos directamente ---
            if mnemonic == "DW":
                for val_tok in tokens[1:]:
                    val_tok = val_tok.rstrip(',')
                    word = self._parse_int(val_tok)
                    emitted.append((n['addr'], word))
                    n['addr'] += self.word_size
                continue

            # --- Directiva RESW: reservar palabras ---
            if mnemonic == "RESW":
                if len(tokens) != 2:
                    raise ValueError("RESW requiere un argumento (cantidad)")
                count = self._parse_int(tokens[1])
                for _ in range(count):
                    emitted.append((n['addr'], 0))
                    n['addr'] += self.word_size
                continue

            # --- Instrucción real: sigue el camino normal ---
            opcode = self.encoder.mnemonic_to_opcode(mnemonic)

            if len(tokens) == 4:  # 3 operandos
                rd = self.encoder.reg_to_num(tokens[1])
                # Soportar I-Type con 3 operandos para ADDI/ST/LD (base+offset)
                if mnemonic == "ADDI":
                    rs1 = self.encoder.reg_to_num(tokens[2])
                    imm_tok = tokens[3].rstrip(',')
                    imm32 = self._parse_int(imm_tok)
                    word = self.encoder.i_type(opcode, rd, rs1, imm32, func=0)
                elif mnemonic == "ST":
                    # ST Rs, Rb, imm  -> func=1 (addr = Rb + signext(imm))
                    rs_src = self.encoder.reg_to_num(tokens[1])  # fuente
                    rb = self.encoder.reg_to_num(tokens[2])      # base
                    imm_tok = tokens[3].rstrip(',')
                    imm32 = self._parse_int(imm_tok)
                    word = self.encoder.i_type(opcode, rd=rb, rs1=rs_src, imm32=imm32, func=1)
                elif mnemonic == "LD":
                    # LD Rd, Rb, imm -> func=1 (addr = Rb + signext(imm))
                    rb = self.encoder.reg_to_num(tokens[2])      # base
                    imm_tok = tokens[3].rstrip(',')
                    imm32 = self._parse_int(imm_tok)
                    word = self.encoder.i_type(opcode, rd=rd, rs1=rb, imm32=imm32, func=1)
                elif mnemonic == "IN":
                    # IN Rd, Rb, count -> func=subop(parse-line) + sep=' '
                    rb = self.encoder.reg_to_num(tokens[2])
                    imm_tok = tokens[3].rstrip(',')
                    imm32 = self._parse_int(imm_tok)
                    func_val = (1 << 1) | (32 << 4)
                    word = self.encoder.i_type(opcode, rd=rd, rs1=rb, imm32=imm32, func=func_val)
                elif mnemonic == "OUT":
                    # OUT Rsrc, imm, func  -> I-Type con func personalizado
                    imm_tok = tokens[2].rstrip(',')
                    imm32 = self._parse_int(imm_tok)
                    func_tok = tokens[3].rstrip(',')
                    func_val = self._parse_int(func_tok)
                    word = self.encoder.i_type(opcode, rd=rd, rs1=0, imm32=imm32, func=func_val)
                else:
                    # R-Type clásico: ADD/SUB/MUL/...
                    rs1 = self.encoder.reg_to_num(tokens[2])
                    rs2 = self.encoder.reg_to_num(tokens[3])
                    word = self.encoder.r_type(opcode, rd, rs1, rs2)

            elif len(tokens) == 3:  # Ej: MOV R1, 0x1000  o  CP R1, R2
                rd = self.encoder.reg_to_num(tokens[1])
                if mnemonic == "CP":
                    # CP Rd, Rs  -> I-Type con registro fuente en RS1 (func=1)
                    rs1 = self.encoder.reg_to_num(tokens[2])
                    word = self.encoder.i_type(opcode, rd, rs1, 0, func=1)
                elif mnemonic == "ST":
                    # ST Rs, [addr] -> I-Type absoluto: rs1=fuente, imm32=addr, func=0
                    rs_src = rd  # primer operando es la fuente
                    imm_tok = tokens[2].rstrip(',')
                    if imm_tok.startswith('[') and imm_tok.endswith(']'):
                        imm_tok = imm_tok[1:-1]
                    imm32 = self._parse_int(imm_tok)
                    word = self.encoder.i_type(opcode, rd=0, rs1=rs_src, imm32=imm32, func=0)
                else:
                    imm_tok = tokens[2].rstrip(',')
                    if imm_tok.startswith('[') and imm_tok.endswith(']'):
                        imm_tok = imm_tok[1:-1]
                    imm32 = self._parse_int(imm_tok)
                    word = self.encoder.i_type(opcode, rd, 0, imm32)

            elif len(tokens) == 2:  # Ej: JMP loop
                imm32 = self._parse_int(tokens[1])
                word = self.encoder.j_type(opcode, imm32)

            else:
                word = self.encoder.s_type(opcode)

            emitted.append((n['addr'], word))
            # Marcar esta dirección como ejecutable (es una instrucción)
            exec_addrs.append(n['addr'])

        # Si se marcó EXEC_FROM, completar un rango continuo desde allí hasta la última instrucción
        if exec_from_addr is not None and exec_addrs:
            last_code_addr = max(exec_addrs)
            a = exec_from_addr & ~0x7  # alinear a 8
            b = last_code_addr
            for addr in range(a, b + self.word_size, self.word_size):
                exec_addrs.append(addr)

        self.write_img(emitted, output_img)
        self.write_exec_map(exec_addrs, output_img + ".exec")

    def write_img(self, pairs: list[tuple[int, int]], output_path: str):
        """
        Genera un archivo .img con pares direccion: valor_hex (64 bits).
        Respeta las direcciones decididas por ORG.
        """
        with open(output_path, "w", encoding="utf-8") as f:
            for addr, word in sorted(pairs, key=lambda x: x[0]):
                f.write(f"0x{addr:08X}: 0x{word:016X}\n")

    def write_exec_map(self, exec_addrs: list[int], path: str):
        """Emite un archivo .exec con una direccion ejecutable por linea."""
        addrs = sorted(set(exec_addrs))
        with open(path, "w", encoding="utf-8") as f:
            for addr in addrs:
                f.write(f"0x{addr:08X}\n")


    def parse_line(self, line: str):
        # quita comentarios '#' y espacios extra
        line = line.split('#', 1)[0].strip()
        if not line:
            return None
        # tokens por espacio; operandos con coma se mantienen (p.ej. "R1,")
        return line.split()

    def _parse_int(self, tok: str) -> int:
        t = tok.strip()
        if t.lower().startswith('0x'):
            return int(t, 16)
        return int(t, 10)

    def _resolve_tokens(self, tokens: list[str]) -> list[str]:
        """
        Sustituye etiquetas por literales hex. Maneja LABEL y [LABEL].
        Conserva comas si el token las trae (p.ej., "R1,").
        """
        out = []
        for tok in tokens:
            has_comma = tok.endswith(',')
            core = tok[:-1] if has_comma else tok

            # Direccionamiento por memoria [LABEL]
            if core.startswith('[') and core.endswith(']'):
                inner = core[1:-1]
                if inner in self.symbols:
                    resolved = f"[0x{self.symbols[inner]:X}]"
                else:
                    resolved = core
            else:
                if core in self.symbols:
                    resolved = f"0x{self.symbols[core]:X}"
                else:
                    resolved = core

            if has_comma:
                resolved += ','
            out.append(resolved)
        return out