import cv2

url = "rtsp://admin:123456789a@192.168.27.57:554/cam/realmonitor?channel=1&subtype=1"

cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

print("camara abierta", cap.isOpened())

# VER LA RESOLUCIÓN QUE ESTÁ RECIBIENDO OPENCV
print("Ancho:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("Alto:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

while True:
    ret, frame = cap.read()

    if not ret:
        print("No se pudo leer la camara")
        break

    cv2.imshow("Camara Dahua", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()