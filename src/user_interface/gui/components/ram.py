from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from src.assembler.assembler import Assembler


class DinamicRandomAccessMemory(ctk.CTkFrame):
    def __init__(self, parent, fg_color="#0c1826", **kwargs):
        super().__init__(parent, fg_color=fg_color)

        self.memory = kwargs.get("memory", None)
        self.cpu = kwargs.get("cpu", None)
        self.apply_icon_path = kwargs.get("apply_icon", None)
        self.load_icon_path = kwargs.get("load_icon", None)

        self.display_mode = 0  # 0 = HEX, 1 = BIN
        self.last_min_addr = 0
        self.last_max_addr = 0
        self.pc_update_callback = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # título
        self.rowconfigure(1, weight=1)  # tabla memoria (se expande)
        self.rowconfigure(2, weight=0)  # controles (compacto)

        self.__load_title_text()
        self.__load_memory_table()
        self.__build_controls()

    def set_pc_update_callback(self, cb):
        """Permite inyectar el callback para refrescar PC en la UI."""
        self.pc_update_callback = cb

    def __load_title_text(self):
        title = ctk.CTkLabel(
            self,
            text="Memoria principal - DRAM",
            font=("Comic Sans MS", 14),
            text_color="white",
        )
        title.grid(column=0, row=0, sticky="w", padx=12, pady=(4, 0))

    def __load_memory_table(self):
        self.memory_textbox = ctk.CTkTextbox(
            self, fg_color="#2b2b2b", font=("Consolas", 12)
        )
        self.memory_textbox.grid(column=0, row=1, sticky="nsew", padx=12, pady=(4, 4))

    def __build_controls(self):
        """Barra de controles compacta en la parte inferior."""
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.grid(column=0, row=2, sticky="ew", padx=12, pady=(0, 12))

        # Layout: switch izquierda, espaciador, botones derecha
        ctrl.columnconfigure(0, weight=0)  # switch
        ctrl.columnconfigure(1, weight=1)  # espaciador
        ctrl.columnconfigure(2, weight=0)  # aplicar
        ctrl.columnconfigure(3, weight=0)  # cargar

        # Toggle HEX/BIN
        self.view_switch = ctk.CTkSwitch(
            ctrl, text="BIN", onvalue=1, offvalue=0, width=80
        )
        self.view_switch.deselect()
        self.view_switch.grid(row=0, column=0, sticky="w")

        def _on_toggle():
            self.display_mode = int(self.view_switch.get())
            self.__reformat_visible_lines()

        self.view_switch.configure(command=_on_toggle)

        # Iconos
        apply_image = None
        load_image = None
        try:
            if self.apply_icon_path:
                apply_image = ctk.CTkImage(
                    light_image=Image.open(self.apply_icon_path),
                    dark_image=Image.open(self.apply_icon_path),
                    size=(24, 24),
                )
            if self.load_icon_path:
                load_image = ctk.CTkImage(
                    light_image=Image.open(self.load_icon_path),
                    dark_image=Image.open(self.load_icon_path),
                    size=(24, 24),
                )
        except Exception:
            pass

        # Botón Aplicar
        apply_btn = ctk.CTkButton(
            ctrl,
            text="Aplicar",
            image=apply_image,
            compound="left",
            command=self.__on_apply_memory_changes,
            fg_color="#4C44AC",
            text_color="white",
            corner_radius=8,
            font=("Comic Sans MS", 12),
            width=100,
            height=32,
        )
        apply_btn.grid(row=0, column=2, padx=(0, 8), sticky="e")

        # Botón Cargar
        load_btn = ctk.CTkButton(
            ctrl,
            text="Cargar",
            image=load_image,
            compound="left",
            command=self.__on_load_absolute_abs,
            fg_color="#4C44AC",
            text_color="white",
            corner_radius=8,
            font=("Comic Sans MS", 12),
            width=100,
            height=32,
        )
        load_btn.grid(row=0, column=3, sticky="e")

    def update_memory(self, memory, min_addr, max_addr):
        self.memory_textbox.delete("1.0", "end")
        self.last_min_addr = min_addr or 0
        self.last_max_addr = max_addr or 0

        # Header
        if self.display_mode == 0:
            header = f"{'Posición':<12} {'Contenido (Hex)'}\n"
        else:
            header = f"{'Posición':<12} {'Contenido (Bin por bytes)'}\n"
        header += "-" * 40 + "\n"

        lines = [header]

        start_word = (min_addr or 0) // 8
        end_word = (max_addr or 0) // 8

        word_pos = start_word
        while word_pos <= end_word:
            addr = word_pos * 8
            value = memory.read_word(addr)
            if self.display_mode == 0:
                fmt = f"0x{value:016X}"
            else:
                bytes_bin = []
                for shift in range(56, -1, -8):
                    b = (value >> shift) & 0xFF
                    bytes_bin.append(f"{b:08b}")
                fmt = " ".join(bytes_bin)
            lines.append(f"{word_pos:<12} {fmt}\n")
            word_pos += 1

        self.memory_textbox.insert("1.0", "".join(lines))

    def __on_apply_memory_changes(self):
        """Parsea el textbox y vuelca a RAM."""
        if not self.memory:
            print("Memoria no disponible")
            return

        content = self.memory_textbox.get("1.0", "end").splitlines()
        modified_positions = set()

        for line in content:
            s = line.strip()
            if not s or s.startswith("Posición") or s.startswith("-"):
                continue
            parts = s.split(maxsplit=1)

            try:
                word_pos = int(parts[0])
            except Exception:
                continue

            if len(parts) < 2 or not parts[1].strip():
                self.memory.write_word(word_pos * 8, 0)
                modified_positions.add(word_pos)
                continue

            data_str = parts[1].strip()
            try:
                val: int
                raw = data_str.strip()
                low = raw.lower()
                cleaned = low.replace(" ", "")

                # BIN
                if cleaned.startswith("0b") or set(cleaned) <= {"0", "1"}:
                    bits = cleaned[2:] if cleaned.startswith("0b") else cleaned
                    if len(bits) > 64:
                        raise ValueError("BIN >64 bits")
                    val = int(bits or "0", 2)
                # HEX
                elif cleaned.startswith("0x") or any(c in "abcdef" for c in cleaned):
                    hx = cleaned[2:] if cleaned.startswith("0x") else cleaned
                    if len(hx) > 16:
                        raise ValueError("HEX >16 dígitos")
                    val = int(hx or "0", 16)
                # DEC
                elif all(c in "0123456789 " for c in raw) and any(
                    ch.isdigit() for ch in raw
                ):
                    dec_clean = raw.replace(" ", "")
                    val = int(dec_clean or "0", 10)
                else:
                    # ASM
                    asm = Assembler()
                    code = f"ORG 0\n{data_str}\n"
                    out = asm.assemble(code).strip()
                    first_line = next(
                        (ln for ln in out.splitlines() if ln.strip()), None
                    )
                    if (
                        not first_line
                        or len(first_line) != 64
                        or not set(first_line) <= {"0", "1"}
                    ):
                        raise ValueError("No se pudo ensamblar la instrucción")
                    val = int(first_line, 2)

                self.memory.write_word(word_pos * 8, val)
                modified_positions.add(word_pos)
            except Exception as e:
                print(f"Línea con error, se setea 0 ({line}): {e}")
                self.memory.write_word(word_pos * 8, 0)
                modified_positions.add(word_pos)

        self.__update_modified_lines(modified_positions)
        print(f"Memoria actualizada: {len(modified_positions)} posiciones modificadas")

    def clear_memory(self):
        """Limpia la visualización de la memoria"""
        self.memory_textbox.delete("1.0", "end")
        header = f"{'Posición':<12} {'Contenido (Hex/Bin)'}\n"
        header += "-" * 40 + "\n"
        self.memory_textbox.insert("1.0", header)

    def __update_modified_lines(self, modified_positions):
        """Actualiza solo las líneas modificadas en el textbox."""
        if not modified_positions or not self.memory:
            return

        content = self.memory_textbox.get("1.0", "end").splitlines()

        for line_idx, line in enumerate(content):
            s = line.strip()
            if not s or s.startswith("Posición") or s.startswith("-"):
                continue

            parts = s.split(maxsplit=1)
            try:
                word_pos = int(parts[0])
            except Exception:
                continue

            if word_pos in modified_positions:
                addr = word_pos * 8
                value = self.memory.read_word(addr)

                if self.display_mode == 0:
                    fmt = f"0x{value:016X}"
                else:
                    bytes_bin = []
                    for shift in range(56, -1, -8):
                        b = (value >> shift) & 0xFF
                        bytes_bin.append(f"{b:08b}")
                    fmt = " ".join(bytes_bin)

                new_line = f"{word_pos:<12} {fmt}"
                tk_line = line_idx + 1
                self.memory_textbox.delete(f"{tk_line}.0", f"{tk_line}.end")
                self.memory_textbox.insert(f"{tk_line}.0", new_line)

    def __reformat_visible_lines(self):
        """Reformatea las líneas visibles al formato actual (HEX/BIN)."""
        if not self.memory:
            return

        content = self.memory_textbox.get("1.0", "end").splitlines()
        new_lines = []

        # Header
        if self.display_mode == 0:
            header = f"{'Posición':<12} {'Contenido (Hex)'}\n"
        else:
            header = f"{'Posición':<12} {'Contenido (Bin por bytes)'}\n"
        header += "-" * 40 + "\n"
        new_lines.append(header)

        for line in content:
            s = line.strip()
            if not s or s.startswith("Posición") or s.startswith("-"):
                continue

            parts = s.split(maxsplit=1)
            try:
                word_pos = int(parts[0])
            except Exception:
                new_lines.append(line + "\n")
                continue

            if len(parts) < 2:
                new_lines.append(line + "\n")
                continue

            addr = word_pos * 8
            value = self.memory.read_word(addr)

            if self.display_mode == 0:
                fmt = f"0x{value:016X}"
            else:
                bytes_bin = []
                for shift in range(56, -1, -8):
                    b = (value >> shift) & 0xFF
                    bytes_bin.append(f"{b:08b}")
                fmt = " ".join(bytes_bin)

            new_lines.append(f"{word_pos:<12} {fmt}\n")

        self.memory_textbox.delete("1.0", "end")
        self.memory_textbox.insert("1.0", "".join(new_lines))

    def refresh_visible(self):
        """API pública para refrescar la vista con los valores actuales de memoria
        sin perder ediciones en curso. Reutiliza el reformateo visible.
        """
        self.__reformat_visible_lines()

    def __on_load_absolute_abs(self):
        """Carga archivo .abs.bin desde dirección 0."""
        if not self.memory:
            print("Memoria no disponible")
            return

        path = filedialog.askopenfilename(
            title="Seleccionar archivo .abs.bin (líneas 64 bits)",
            filetypes=[("ABS Bin", "*.abs.bin"), ("Texto", "*.txt"), ("Todos", "*.*")],
        )
        if not path:
            return

        wrote = 0
        try:
            addr = 0
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for raw in f:
                    line = raw.strip()
                    if not line:
                        continue
                    norm = line.replace(" ", "")
                    if not set(norm) <= {"0", "1"} or len(norm) != 64:
                        raise ValueError(
                            f"Línea no válida (esperado 64 bits binarios): {line}"
                        )
                    val = int(norm, 2)
                    if addr > self.memory.size - 8:
                        raise ValueError("Archivo excede el tamaño de la memoria")
                    self.memory.write_word(addr, val)
                    addr += 8
                    wrote += 1

            self.update_memory(self.memory, self.last_min_addr, self.last_max_addr)
            print(f"OK: {wrote} palabras cargadas desde 0 en RAM")
        except Exception as e:
            print(f"Error al cargar absoluto: {e}")
