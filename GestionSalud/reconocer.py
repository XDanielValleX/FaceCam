import cv2
import face_recognition
import numpy as np
from datetime import datetime, timedelta

from db import conectar
from personas import cargar_personas
from rtsp_camera import abrir_camara
from config import *


# ==================================
# CONEXION POSTGRESQL
# ==================================

try:

    conn = conectar()

    cursor = conn.cursor()

    print("Conectado a PostgreSQL")

except Exception as e:

    print("Error PostgreSQL:", e)

    exit()


# ==================================
# CARGAR PERSONAS
# ==================================

caras_conocidas, nombres = cargar_personas()


# ==================================
# CONTROL DE DUPLICADOS
# ==================================

ultimas_detecciones = {}


# ==================================
# CAMARA
# ==================================

indice_camara = 0

NOMBRE_CAMARA = CAMARAS[indice_camara]["nombre"]

RTSP_URL = CAMARAS[indice_camara]["rtsp"]

cap = abrir_camara(RTSP_URL)

if cap is None:

    print("No se pudo abrir la camara")

    exit()

print("Camara conectada")
print("Camara actual:", NOMBRE_CAMARA)


# ==================================
# LOOP PRINCIPAL
# ==================================

while True:

    ret, frame = cap.read()

    if not ret:

        print("Error leyendo camara")

        break

    frame = np.array(frame, dtype=np.uint8)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    ubicaciones = face_recognition.face_locations(rgb)

    encodings = face_recognition.face_encodings(
        rgb,
        ubicaciones
    )

    for (top, right, bottom, left), encoding in zip(
        ubicaciones,
        encodings
    ):

        nombre = "Desconocido"

        coincidencias = face_recognition.compare_faces(
            caras_conocidas,
            encoding
        )

        if True in coincidencias:

            indice = coincidencias.index(True)

            nombre = nombres[indice]

            ahora = datetime.now()

            guardar = False

            if nombre not in ultimas_detecciones:

                guardar = True

            else:

                diferencia = ahora - ultimas_detecciones[nombre]

                if diferencia > timedelta(
                    seconds=TIEMPO_REPETICION
                ):

                    guardar = True

            if guardar:

                try:

                    # ==========================
                    # BUSCAR ID DE LA PERSONA
                    # ==========================

                    cursor.execute(
                        """
                        SELECT id
                        FROM personas
                        WHERE nombre = %s
                        """,
                        (nombre,)
                    )

                    resultado_persona = cursor.fetchone()

                    if resultado_persona is None:

                        print("La persona no existe en la tabla personas")

                    else:

                        persona_id = resultado_persona[0]

                        # ==========================
                        # BUSCAR ID DE LA CAMARA
                        # ==========================

                        cursor.execute(
                            """
                            SELECT id
                            FROM camaras
                            WHERE nombre = %s
                            """,
                            (NOMBRE_CAMARA,)
                        )

                        resultado_camara = cursor.fetchone()

                        if resultado_camara is None:

                            print("La camara no existe en la tabla camaras")

                        else:

                            camara_id = resultado_camara[0]

                            # ==========================
                            # INSERTAR DETECCION
                            # ==========================

                            cursor.execute(
                                """
                                INSERT INTO detecciones
                                (
                                    persona_id,
                                    camara_id,
                                    fecha_hora
                                )
                                VALUES
                                (
                                    %s,
                                    %s,
                                    %s
                                )
                                """,
                                (
                                    persona_id,
                                    camara_id,
                                    ahora
                                )
                            )

                            conn.commit()

                            ultimas_detecciones[nombre] = ahora

                            print(
                                f"[OK] {nombre} | "
                                f"{NOMBRE_CAMARA} | "
                                f"{ahora.strftime('%Y-%m-%d %H:%M:%S')}"
                            )

                except Exception as e:

                    conn.rollback()

                    print("Error insertando:", e)

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

    # ESC
    if tecla == 27:

        break

    # Siguiente camara
    if tecla == ord("n"):

        indice_camara += 1

        if indice_camara >= len(CAMARAS):

            indice_camara = 0

        cap.release()

        NOMBRE_CAMARA = CAMARAS[indice_camara]["nombre"]

        RTSP_URL = CAMARAS[indice_camara]["rtsp"]

        cap = abrir_camara(RTSP_URL)

        print()
        print("=================================")
        print("Cambiando a:", NOMBRE_CAMARA)
        print("=================================")


# ==================================
# CIERRE
# ==================================

cap.release()

cursor.close()

conn.close()

cv2.destroyAllWindows()