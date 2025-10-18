from src.loader.linker_loader_new import Linker, Loader

def link(lines):
    return Linker().link(lines = lines)

def load(memory, lines):
    cargador = Loader(memory = memory)
    min_addr, max_addr = cargador.load(lines = lines)
    print(min_addr, max_addr)
    return min_addr, max_addr

def get_textbox_lines(textbox):
    contenido = textbox.get('1.0', 'end')
    return contenido.strip().split('\n')

def link_load(textbox, memory):
    with open('memory_test.txt', 'w') as f:
        for _ in memory.get_content_list():
            print(_, file=f)
    contenido = get_textbox_lines(textbox)
    if link(contenido):
        print("enlazado")
        load(memory, contenido)
        # print(memory.get_content_list())
    else:
        print('\033[33m No se pudo enlazar \033[0m')

