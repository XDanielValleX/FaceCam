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

    for archivo in os.listdir(ruta_personas):

        ruta_imagen = os.path.join(
            ruta_personas,
            archivo
        )

        try:

            imagen = cv2.imread(ruta_imagen)

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
                continue

            caras_conocidas.append(
                encodings[0]
            )

            nombre = os.path.splitext(
                archivo
            )[0]

            nombres.append(nombre)

            print(nombre, "cargado")

        except Exception as e:

            print(
                "Error cargando",
                archivo,
                e
            )

    print()
    print("Personas cargadas:")
    print(nombres)

    return caras_conocidas, nombres