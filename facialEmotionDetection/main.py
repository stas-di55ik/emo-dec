import cv2
import matplotlib.pyplot as plt
from deepface import DeepFace

img = cv2.imread('test1.jpg')
plt.imshow(img)

predictions = DeepFace.analyze(img)
print(predictions)

# faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_defult.xml')
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# faces = faceCascade.detectMultiScale(gray, 1.1, 4)
# for (x, y, w, h) in faces:
#     cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
# plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
# plt.show()
