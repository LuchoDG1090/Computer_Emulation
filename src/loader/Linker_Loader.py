from typing import Tuple
import os

import src.user_interface.logging.logger as logger

logger_handler = logger.configurar_logger()

class Linker:
    """Es el encargado de revisar un archivo .img recibido por parte del modulo anterior, 
    donde una tiene el nombre de la instrucción y la otra una lista de enteros
    """

    @staticmethod
    def revisar_img(path: str) -> bool:
        """
        Verifica que un archivo .img sea válido.
        Retorna True si todo está bien, o lanza ValueError con el error.
        """
        if not os.path.exists(path):
            logger_handler.error("El archivo indicado no existe")
            raise FileNotFoundError(f"No existe el archivo {path}")

        with open(path, "r") as f:
            logger_handler.info("Apertura del archivo .img para el procesamiento por parte del enlazador-cargador")
            for linea_no, raw in enumerate(f, 1):
                # quitar comentarios y espacios
                linea = raw.split("#", 1)[0].strip()
                if linea == "":
                    continue

                if ":" not in linea:
                    raise ValueError(f"Línea {linea_no}: falta ':' (dirección: instrucciones)")

                dir_txt, instr_txt = linea.split(":", 1)
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
                    except ValueError:
                        raise ValueError(f"Línea {linea_no}: instrucción inválida '{w}'")

        return True

class Loader:

    @staticmethod
    def hex_instruccion(instruccion:str) -> int:
        """
        Elimina prefijos, revisa que la instrucción no esté vacía y que no sea muy larga.
        convierte la instrucción a entero.
        """
        instruccion = instruccion.strip()
        if instruccion.startswith('0x') or instruccion.startswith('0X'):
            instruccion = instruccion[2:]
        instruccion = instruccion.strip(',;')
        if instruccion == '':
            logger_handler.error("Error con la instrucción, esta se encuentra vacía")
            raise ValueError("Instrucción vacía")
        if len(instruccion) > 16:
            logger_handler.error("La longitud de la instrucción supera el valor máximo estandarizado")
            raise ValueError(f"La instrucción es demasiado larga")
        return int(instruccion,16) & 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def leer_img(memory, path: str, dir_base: int = None) -> Tuple[int,int]:
        """
        Lee el archivo .img y carga las instrucciones en memoria (palabras de 64 bits).
        Retorna (min_addr, max_addr) cargadas en bytes.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"No existe el documento {path}")
        dir_sig = dir_base
        min_dir = None
        max_dir = None

        with open(path, 'r') as f:
            for linea_no, instruccion in enumerate(f,1):
                linea = instruccion.split('#',1)[0].strip()
                if linea == '':
                    continue
                if ':' in linea:
                    izq, der = linea.split(':',1)
                    izq = izq.strip() 
                    der = der.strip()
                    if izq == '':
                        if dir_sig is None:
                            logger_handler.error(f"No se brindó una dirección para la instrucción en la linea: {linea_no}")
                            raise ValueError(f"No se brindó una dirección para la instrucción en la linea {linea_no}")
                        dir = dir_sig
                    else:
                        dir = int(izq,0)
                        dir_sig = dir
                    words = [w.strip() for w in der.split(',') if w.strip() != '']
                else:
                    if dir_sig is None:
                        raise ValueError(f"No se brindó una dirección explicita para la instrucción en la linea {linea_no}")
                    dir = dir_sig
                    words = [w.strip() for w in linea.split(',') if w.strip() != '']
                
                for w in words:
                    value = Loader.hex_instruccion(w) & 0xFFFFFFFFFFFFFFFF
                    memory.write_word(dir, value)  # escribe palabra de 64 bits
                    if min_dir is None or dir < min_dir:
                        min_dir = dir
                    if max_dir is None or dir > max_dir:
                        max_dir = dir
                    dir += 8                     # avanzar 8 bytes por palabra de 64 bits
                    dir_sig = dir
        return (min_dir if min_dir is not None else 0, max_dir if max_dir is not None else -1)
        
