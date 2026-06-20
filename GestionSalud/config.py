from dotenv import load_dotenv
import os

load_dotenv()

RTSP_URL = os.getenv("RTSP_URL")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

NOMBRE_CAMARA = "Consultorio_1"

TIEMPO_REPETICION = 30