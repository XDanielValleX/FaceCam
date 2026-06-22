import cv2
import face_recognition
import numpy as np
import threading

from datetime import datetime, timedelta

from database.db import conectar
from recognition.personas import cargar_personas
from recognition.detector import detectar_rostros
from camaras.rtsp_camera import abrir_camara

from services.personas_service import buscar_persona_id
from services.camaras_service import buscar_camara_id
from services.detecciones_service import guardar_deteccion

from logs.logger import escribir_log
from logs.logger import escribir_error

from config.config import *


def iniciar_reconocimiento():

    try:

        conn = conectar()

        cursor = conn.cursor()

        print("Conectado a PostgreSQL")

    except Exception as e:

        escribir_error(e)

        print("Error PostgreSQL:", e)

        return

    caras_conocidas, nombres = cargar_personas()

    ultimas_detecciones = {}

    camara_actual = CAMARAS[0]

    cap = abrir_camara(
        camara_actual["rtsp"]
    )

    if cap is None:

        mensaje = (
            f"No se pudo abrir la camara "
            f"{camara_actual['nombre']}"
        )

        escribir_error(mensaje)

        print(mensaje)

        return

    cap.set(
        cv2.CAP_PROP_BUFFERSIZE,
        1
    )

    print("Camara conectada")

    # ==================================
    # HILO DE CAPTURA
    # ==================================

    frame_actual = None

    lock = threading.Lock()

    def actualizar_frame():

        nonlocal frame_actual

        while True:

            ret, frame = cap.read()

            if ret:

                with lock:

                    frame_actual = frame

    hilo = threading.Thread(
        target=actualizar_frame,
        daemon=True
    )

    hilo.start()

    # ==================================
    # LOOP PRINCIPAL
    # ==================================

    contador_frames = 0

    ubicaciones = []

    encodings = []

    while True:

        with lock:

            if frame_actual is None:

                continue

            frame = frame_actual.copy()

        contador_frames += 1

        # Procesar solo 1 de cada 3 frames
        if contador_frames % 10 == 0:

            frame = np.array(
                frame,
                dtype=np.uint8
            )

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            ubicaciones, encodings = detectar_rostros(
                rgb
            )

        for (
            top,
            right,
            bottom,
            left
        ), encoding in zip(
            ubicaciones,
            encodings
        ):

            nombre = "Desconocido"

            coincidencias = face_recognition.compare_faces(
                caras_conocidas,
                encoding
            )

            if True in coincidencias:

                indice = coincidencias.index(
                    True
                )

                nombre = nombres[indice]

                ahora = datetime.now()

                guardar = False

                if nombre not in ultimas_detecciones:

                    guardar = True

                else:

                    diferencia = (
                        ahora -
                        ultimas_detecciones[nombre]
                    )

                    guardar = (
                        diferencia >
                        timedelta(
                            seconds=TIEMPO_REPETICION
                        )
                    )

                if guardar:

                    try:

                        persona_id = buscar_persona_id(
                            cursor,
                            nombre
                        )

                        camara_id = buscar_camara_id(
                            cursor,
                            camara_actual["nombre"]
                        )

                        if (
                            persona_id is not None
                            and
                            camara_id is not None
                        ):

                            guardar_deteccion(
                                cursor,
                                conn,
                                persona_id,
                                camara_id,
                                ahora
                            )

                            ultimas_detecciones[
                                nombre
                            ] = ahora

                            mensaje = (
                                f"{nombre} detectado en "
                                f"{camara_actual['nombre']}"
                            )

                            print(
                                f"[OK] {nombre}"
                            )

                            escribir_log(
                                mensaje
                            )

                        else:

                            escribir_error(
                                f"No existe persona o camara: {nombre}"
                            )

                    except Exception as e:

                        conn.rollback()

                        escribir_error(e)

                        print(
                            "Error insertando:",
                            e
                        )

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                nombre,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        cv2.imshow(
            "Reconocimiento Facial",
            frame
        )

        tecla = cv2.waitKey(1)

        if tecla == 27:

            break

    cap.release()

    cursor.close()

    conn.close()

    cv2.destroyAllWindows()