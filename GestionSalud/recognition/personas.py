import cv2
import face_recognition
import numpy as np
import os


def cargar_personas():

    ruta_personas = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        "personas"
    )

    caras_conocidas = []

    nombres = []

    for nombre_persona in os.listdir(ruta_personas):

        carpeta_persona = os.path.join(
            ruta_personas,
            nombre_persona
        )

        if not os.path.isdir(carpeta_persona):

            continue

        for archivo in os.listdir(carpeta_persona):

            ruta_imagen = os.path.join(
                carpeta_persona,
                archivo
            )

            try:

                imagen = cv2.imread(
                    ruta_imagen
                )

                if imagen is None:

                    continue

                imagen = cv2.cvtColor(
                    imagen,
                    cv2.COLOR_BGR2RGB
                )

                imagen = np.array(
                    imagen,
                    dtype=np.uint8
                )

                encodings = face_recognition.face_encodings(
                    imagen
                )

                if len(encodings) == 0:

                    print(
                        "No se detectó rostro en:",
                        archivo
                    )

                    continue

                caras_conocidas.append(
                    encodings[0]
                )

                nombres.append(
                    nombre_persona
                )

                print(
                    nombre_persona,
                    "-",
                    archivo,
                    "cargado"
                )

            except Exception as e:

                print(
                    "Error cargando",
                    archivo,
                    e
                )

    print()

    print("Personas cargadas:")

    print(
        list(
            set(nombres)
        )
    )

    return caras_conocidas, nombres