"""Preprocesador para código fuente ensamblador"""

import re


def convert_org_word_positions_to_bytes(source: str) -> str:
    """
    Convierte directivas ORG decimales de posiciones de palabra a direcciones en bytes.

    Esto permite a los programadores pensar en términos de posiciones de palabras de 64 bits
    mientras el ensamblador trabaja internamente con direcciones en bytes.

    Ejemplos:
        ORG 2500 -> ORG 20000  (palabra 2500 = byte 20000)
        ORG 0xF000 -> ORG 0xF000 (hexadecimal sin cambios)

    Args:
        source: Código fuente ensamblador

    Returns:
        Código preprocesado con valores ORG decimales multiplicados por 8
    """
    lines = source.splitlines()
    out_lines = []

    for line in lines:
        # Separar código de comentarios
        code, sep, comment = line.partition("#")

        # Coincidir ORG con número decimal (no hexadecimal)
        match = re.match(r"^(\s*ORG\s+)(\d+)(\s*)$", code)
        if match:
            word_position = int(match.group(2))
            byte_address = word_position * 8
            new_code = f"{match.group(1)}{byte_address}{match.group(3)}"
            out_lines.append(new_code + (sep + comment if sep else ""))
        else:
            out_lines.append(line)

    return "\n".join(out_lines)
