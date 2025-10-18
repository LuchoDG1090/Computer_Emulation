from typing import Tuple
import src.memory.memory as mem

# import src.user_interface.logging.logger as logger

# logger_handler = logger.configurar_logger()

def load_lines_img(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.readlines()

class Linker:
    """Es el encargado de revisar un archivo .img recibido por parte del modulo anterior, 
    donde una tiene el nombre de la instrucción y la otra una lista de enteros
    """

    def __process_lines(self, lines: list[str]):
        for linea_no, raw in enumerate(lines, 1):
            linea = raw.split("#", 1)[0].strip()
            if linea == "":
                continue

            if ':' not in linea:
                raise ValueError(f'Linea {linea_no}: falta \':\' (direccion:instrucciones)')

            dir_txt, instr_txt = linea.split(':', 1)
            dir_txt = dir_txt.strip()
            instr_txt = instr_txt.strip()

            # validar dirección
            try:
                direccion = int(dir_txt, 0)  # base 0 detecta 0x..., dec...
            except ValueError:
                raise ValueError(f"Línea {linea_no}: dirección inválida '{dir_txt}'")
            
            # validar instrucciones
            instrucciones = [w.strip() for w in instr_txt.split(",") if w.strip()]
            for w in instrucciones:
                try:
                    val = int(w, 16)
                    if val > 0xFFFFFFFFFFFFFFFF:
                        raise ValueError(f"Línea {linea_no}: instrucción fuera de rango 64 bits '{w}'")
                except ValueError as e:
                    raise ValueError(f"Línea {linea_no}: instrucción inválida '{w}' {str(e)}")
        return True

    def link(self, origin: str = None, lines: list = None):
        if not origin and not lines:
            raise RuntimeError("El número de argumentos pasados a la función no es correcto")
        if origin:
            lines = load_lines_img(origin)
        return self.__process_lines(lines)

class Loader:
    def __init__(self, memory: mem.Memory ,dir_base: int = None):
        self.dir_sig = dir_base
        self.min_dir = None
        self.max_dir = None
        self.memory = memory

    def __hex_instruccion(self, instruccion:str) -> int:
        """
        Elimina prefijos, revisa que la instrucción no esté vacía y que no sea muy larga.
        convierte la instrucción a entero.
        """
        instruccion = instruccion.strip()
        if instruccion.lower().startswith('0x'):
            instruccion = instruccion[2:]
        instruccion = instruccion.strip(',;')
        if instruccion == '':
            raise ValueError("Instrucción vacía")
        if len(instruccion) > 16:
            raise ValueError(f"La instrucción es demasiado larga")
        return int(instruccion,16) & 0xFFFFFFFFFFFFFFFF
    
    def __process_img(self, lines: list[str]) -> Tuple[int,int]:
        for linea_no, instruccion in enumerate(lines, 1):
            linea = instruccion.split('#',1)[0].strip()
            if linea == '':
                continue
            if ':' in linea:
                izq, der = linea.split(':',1)
                izq = izq.strip() 
                der = der.strip()
                if izq == '':
                    if not self.dir_sig:
                        raise ValueError(f"No se brindó una dirección para la instrucción en la linea {linea_no}")
                    dir = self.dir_sig
                else:
                    dir = int(izq, 0)
                    self.dir_sig = dir
                words = [w.strip() for w in der.split(',') if w.strip() != '']
            else:  
                if self.dir_sig is None:
                    raise ValueError(f"No se brindó una dirección explicita para la instrucción en la linea {linea_no}")
                dir = self.dir_sig
                words = [w.strip() for w in linea.split(',') if w.strip() != '']
            
            for w in words:
                value = self.__hex_instruccion(w) & 0xFFFFFFFFFFFFFFFF
                self.memory.write_word(dir, value)  # escribe palabra de 64 bits
                if self.min_dir is None or dir < self.min_dir:
                    self.min_dir = dir
                if self.max_dir is None or dir > self.max_dir:
                    self.max_dir = dir
                dir += 8                     # avanzar 8 bytes por palabra de 64 bits
                self.dir_sig = dir
        return (self.min_dir if self.min_dir is not None else 0, self.max_dir if self.max_dir is not None else -1)
    
    def load(self, origin: str = None, lines: list = None):
        if not origin and not lines:
            raise RuntimeError("El número de argumentos pasados a la función no es correcto")
        if origin:
            lines = load_lines_img(origin)
        return self.__process_img(lines)
        