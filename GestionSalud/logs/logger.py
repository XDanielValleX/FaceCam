import logging
import os

ruta_logs = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sistema.log"
)

logging.basicConfig(
    filename=ruta_logs,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def escribir_log(mensaje):

    logging.info(mensaje)


def escribir_error(error):

    logging.error(error)