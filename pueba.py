import cv2
import face_recognition
import numpy as np

img = cv2.imread("personas/Cristian Jimenez.jpeg")

rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

rgb = np.array(rgb, dtype=np.uint8)

print(rgb.dtype)
print(rgb.flags)

caras = face_recognition.face_locations(rgb)

print(caras)