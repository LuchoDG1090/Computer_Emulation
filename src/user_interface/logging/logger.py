import logging
import logging.handlers
import os
import sys

def configurar_logger(nombre_app="euclid_64_logs", log_dir="logs", nivel=logging.DEBUG):
    os.makedirs(log_dir, exist_ok=True)

    formato = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger(nombre_app)
    logger.setLevel(nivel)

    if not logger.handlers:

        archivo = logging.handlers.TimedRotatingFileHandler(
            os.path.join(log_dir, f"{nombre_app}.log"),
            when="midnight",
            backupCount=7,
            encoding="utf-8"
        )
        archivo.setLevel(logging.DEBUG)
        archivo.setFormatter(formato)
        logger.addHandler(archivo)

    return logger