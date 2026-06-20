import cv2

url = "rtsp://admin:123456789a@192.168.27.57:554/cam/realmonitor?channel=1&subtype=1"

cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

# Clasificador de rostros de OpenCV
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rostros = face_cascade.detectMultiScale(
        gris,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30,30)
    )

    for (x, y, w, h) in rostros:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

    cv2.imshow("Deteccion de Rostros", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()