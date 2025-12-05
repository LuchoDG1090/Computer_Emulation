"""
Gestor de Disco Virtual (disk.img)

Herramienta CLI para administrar programas ensamblador en el disco virtual.

Uso:
    python disk_manager.py format              - Formatear disco
    python disk_manager.py write <name> <file> - Escribir programa
    python disk_manager.py read <name>         - Leer programa
    python disk_manager.py list                - Listar programas
    python disk_manager.py info                - Información del disco
    python disk_manager.py delete <name>       - Eliminar programa
    python disk_manager.py compact             - Compactar disco

Ejemplos:
    # Escribir programa al disco
    python disk_manager.py write math includes/math.asm
    
    # Listar todos los programas
    python disk_manager.py list
    
    # Leer programa y guardar
    python disk_manager.py read math -o math_backup.asm

Autor: Computer Emulation Project
"""

import sys
import os
import argparse
from datetime import datetime

# Añadir directorio raíz al path
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.disk.simple_disk import SimpleDisk


def format_size(bytes_size):
    """Formatea tamaño en bytes a KB/MB"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


def cmd_format(args):
    """Formatea el disco"""
    if os.path.exists(args.disk):
        response = input(f"  '{args.disk}' ya existe. ¿Sobrescribir? (s/N): ")
        if response.lower() != 's':
            print(" Operación cancelada")
            return
    
    disk = SimpleDisk(args.disk)
    disk._format_disk()
    print(f" Disco '{args.disk}' formateado exitosamente")


def cmd_write(args):
    """Escribe programa al disco"""
    if not os.path.exists(args.file):
        print(f" Error: Archivo '{args.file}' no encontrado")
        return
    
    disk = SimpleDisk(args.disk)
    
    with open(args.file, 'r', encoding='utf-8') as f:
        asm_code = f.read()
    
    try:
        if disk.write_program(args.name, asm_code):
            print(f" Programa '{args.name}' escrito exitosamente")
            info = disk.get_program_info(args.name)
            print(f"   Tamaño: {format_size(info['size'])}, Líneas: {info['lines']}")
    except Exception as e:
        print(f" Error al escribir '{args.name}': {e}")


def cmd_read(args):
    """Lee programa desde disco"""
    disk = SimpleDisk(args.disk)
    
    code = disk.read_program(args.name)
    
    if code is None:
        print(f" Programa '{args.name}' no encontrado en disco")
        return
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f" Programa '{args.name}' guardado en '{args.output}'")
    else:
        print(f"\n{'='*60}")
        print(f"Programa: {args.name}")
        print(f"{'='*60}\n")
        print(code)
        print(f"\n{'='*60}")


def cmd_delete(args):
    """Elimina programa del disco"""
    disk = SimpleDisk(args.disk)
    
    if not disk.program_exists(args.name):
        print(f" Programa '{args.name}' no encontrado")
        return
    
    if not args.force:
        response = input(f"  ¿Eliminar '{args.name}'? (s/N): ")
        if response.lower() != 's':
            print(" Operación cancelada")
            return
    
    if disk.delete_program(args.name):
        print(f" Programa '{args.name}' eliminado")
        print(" Usa 'compact' para liberar espacio físico")
    else:
        print(f" Error al eliminar '{args.name}'")


def cmd_list(args):
    """Lista programas en disco"""
    disk = SimpleDisk(args.disk)
    programs = disk.list_programs()
    
    if not programs:
        print(" Disco vacío - No hay programas almacenados")
        return
    
    print(f"\n{'='*80}")
    print(f"{'Programa':<30} {'Tamaño':<12} {'Líneas':<8} {'Fecha':<20}")
    print(f"{'='*80}")
    
    for prog in programs:
        date_str = datetime.fromisoformat(prog['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{prog['name']:<30} {format_size(prog['size']):<12} {prog['lines']:<8} {date_str:<20}")
    
    print(f"{'='*80}")
    print(f" Total: {len(programs)} programa(s)")


def cmd_info(args):
    """Muestra información del disco"""
    if not os.path.exists(args.disk):
        print(f" Disco '{args.disk}' no existe")
        print(f" Usa 'format' para crear uno nuevo")
        return
    
    disk = SimpleDisk(args.disk)
    programs = disk.list_programs()
    
    total_size = os.path.getsize(args.disk)
    header_size = SimpleDisk.HEADER_SIZE
    data_size = total_size - header_size
    used_size = sum(p['size'] for p in programs)
    free_size = data_size - used_size
    
    print(f"\n{'='*60}")
    print(f" Información del Disco: {args.disk}")
    print(f"{'='*60}")
    print(f"Tamaño total:      {format_size(total_size)}")
    print(f"Header (índice):   {format_size(header_size)}")
    print(f"Datos:             {format_size(data_size)}")
    print(f"  └─ Usados:       {format_size(used_size)} ({used_size/data_size*100:.1f}%)")
    print(f"  └─ Libres:       {format_size(free_size)} ({free_size/data_size*100:.1f}%)")
    print(f"Programas:         {len(programs)}")
    
    if programs:
        total_lines = sum(p['lines'] for p in programs)
        print(f"Total líneas:      {total_lines}")
    
    print(f"{'='*60}\n")


def cmd_compact(args):
    """Compacta el disco"""
    disk = SimpleDisk(args.disk)
    
    print("🔧 Iniciando compactación...")
    freed = disk.compact_disk()
    
    if freed > 0:
        print(f" Compactación completada: {format_size(freed)} liberados")
    else:
        print("ℹ  No hay espacio para liberar")


def main():
    parser = argparse.ArgumentParser(
        description="Gestor de Disco Virtual (.img) para programas ensamblador",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s format
  %(prog)s write math includes/math.asm
  %(prog)s list
  %(prog)s read math -o backup.asm
  %(prog)s info
  %(prog)s delete old_program
  %(prog)s compact
        """
    )
    
    parser.add_argument(
        '--disk',
        default='disk.img',
        help='Archivo de disco (default: disk.img)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: format
    subparsers.add_parser('format', help='Formatear disco (elimina todo)')
    
    # Comando: write
    write_parser = subparsers.add_parser('write', help='Escribir programa al disco')
    write_parser.add_argument('name', help='Nombre del programa')
    write_parser.add_argument('file', help='Archivo .asm a escribir')
    
    # Comando: read
    read_parser = subparsers.add_parser('read', help='Leer programa desde disco')
    read_parser.add_argument('name', help='Nombre del programa')
    read_parser.add_argument('-o', '--output', help='Guardar en archivo')
    
    # Comando: delete
    delete_parser = subparsers.add_parser('delete', help='Eliminar programa')
    delete_parser.add_argument('name', help='Nombre del programa')
    delete_parser.add_argument('-f', '--force', action='store_true', help='No pedir confirmación')
    
    # Comando: list
    subparsers.add_parser('list', help='Listar programas en disco')
    
    # Comando: info
    subparsers.add_parser('info', help='Mostrar información del disco')
    
    # Comando: compact
    subparsers.add_parser('compact', help='Compactar disco (liberar espacio)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        'format': cmd_format,
        'write': cmd_write,
        'read': cmd_read,
        'delete': cmd_delete,
        'list': cmd_list,
        'info': cmd_info,
        'compact': cmd_compact
    }
    
    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\n\n  Operación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
