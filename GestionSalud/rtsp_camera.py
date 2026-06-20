import cv2

def abrir_camara(url):

    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        return None

    return cap