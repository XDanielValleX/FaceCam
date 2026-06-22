from dotenv import load_dotenv
import os

load_dotenv()

# ==========================
# BASE DE DATOS
# ==========================

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ==========================
# CAMARAS
# ==========================

CAMARAS = [

    {
        "nombre": "Consultorio_1",
        "rtsp": os.getenv("RTSP_CAMARA_1")
    },

    {
        "nombre": "Consultorio_2",
        "rtsp": os.getenv("RTSP_CAMARA_2")
    },

    {
        "nombre": "Recepcion",
        "rtsp": os.getenv("RTSP_CAMARA_3")
    }

]

# ==========================
# TIEMPO ENTRE REGISTROS
# ==========================

TIEMPO_REPETICION = 30