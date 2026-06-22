import face_recognition


def detectar_rostros(rgb):

    ubicaciones = face_recognition.face_locations(
        rgb
    )

    encodings = face_recognition.face_encodings(
        rgb,
        ubicaciones
    )

    return ubicaciones, encodings