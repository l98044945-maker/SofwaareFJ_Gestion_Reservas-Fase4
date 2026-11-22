import logging
import os


def configurar_logger(ruta_archivo: str = "logs/eventos_software_fj.log") -> logging.Logger:
    directorio = os.path.dirname(ruta_archivo)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)

    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(module)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        manejador_archivo = logging.FileHandler(ruta_archivo, mode="a", encoding="utf-8")
        manejador_archivo.setFormatter(formato)
        logger.addHandler(manejador_archivo)

        manejador_consola = logging.StreamHandler()
        manejador_consola.setFormatter(formato)
        logger.addHandler(manejador_consola)

    return logger
