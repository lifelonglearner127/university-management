import argparse
import cv2
import face_recognition


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

image = cv2.imread(args["image"])
face_locations = face_recognition.face_locations(image, model="hog")
for face_location in face_locations:
    (top, right, bottom, left) = face_location
    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

cv2.imshow("image", image)
cv2.waitKey(0)
