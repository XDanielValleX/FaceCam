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

    # =====================================
    # CAMARAS IP INDEPENDIENTES
    # =====================================

    {
        "nombre": "Consultorio_1",

        "tipo": "IP",

        "rtsp": os.getenv(
            "RTSP_CAMARA_1"
        )
    },

    {
        "nombre": "Consultorio_2",

        "tipo": "IP",

        "rtsp": os.getenv(
            "RTSP_CAMARA_2"
        )
    },


    # =====================================
    # CAMARAS DEL NVR 1
    # =====================================

    {
        "nombre": "Recepcion",

        "tipo": "NVR",

        "nvr": 1,

        "canal": 1
    },

    {
        "nombre": "Laboratorio",

        "tipo": "NVR",

        "nvr": 1,

        "canal": 2
    },


    # =====================================
    # CAMARAS DEL NVR 2
    # =====================================

    {
        "nombre": "Urgencias",

        "tipo": "NVR",

        "nvr": 2,

        "canal": 1
    },

    {
        "nombre": "Farmacia",

        "tipo": "NVR",

        "nvr": 2,

        "canal": 2
    }

]


# ==========================
# GENERAR RTSP DE LOS NVR
# ==========================

for camara in CAMARAS:

    if camara["tipo"] == "NVR":

        numero_nvr = camara["nvr"]

        ip = os.getenv(
            f"NVR{numero_nvr}_IP"
        )

        usuario = os.getenv(
            f"NVR{numero_nvr}_USUARIO"
        )

        password = os.getenv(
            f"NVR{numero_nvr}_PASSWORD"
        )

        camara["rtsp"] = (

            f"rtsp://"

            f"{usuario}:"

            f"{password}@"

            f"{ip}:554/"

            f"cam/realmonitor?"

            f"channel={camara['canal']}"

            f"&subtype=1"

        )


# ==========================
# TIEMPO ENTRE REGISTROS
# ==========================

TIEMPO_REPETICION = 30