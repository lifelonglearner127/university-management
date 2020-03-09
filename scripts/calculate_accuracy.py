import argparse
import os
import random
import cv2
import face_recognition
from imutils import paths


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True, help="Path to the face dataset")
ap.add_argument("-n", "--num", required=True, type=int, help="Number of images")
args = vars(ap.parse_args())

persons = [person for person in os.listdir(args["dataset"]) if os.path.isdir(os.path.join(args["dataset"], person))]
test_images = []
encodings = {}

print(f"[INFO] gathering one test file and encoding from {args['num']} training files")
for (i, person) in enumerate(persons):
    image_paths = list(paths.list_images(os.path.join(args["dataset"], person)))
    random.shuffle(image_paths)

    print(f"[INFO] encoding {i + 1}th faces")
    encodings[person] = []
    image_nums = 0
    for image_path in image_paths:
        image = cv2.imread(image_path)
        face_locations = face_recognition.face_locations(image, model="hog")
        if len(face_locations) != 1:
            print(f"Could not detect face from this file {image_path}")
            continue

        if len(test_images) == i:
            test_images.append(image_path)
            continue

        if image_nums >= args["num"]:
            break

        image_nums += 1
        (top, right, bottom, left) = face_locations[0]
        detected_face = image[top:bottom, left:right]
        encodings[person].append(face_recognition.face_encodings(detected_face)[0])


false_positives = 0
false_negatives = 0
true_positives = 0
true_negatives = 0

print("[INFO] Evaluating")
for (i, person) in enumerate(persons):
    for (j, test_image) in enumerate(test_images):
        query_image = face_recognition.load_image_file(test_image)
        face_locations = face_recognition.face_locations(query_image, model="hog")
        (top, right, bottom, left) = face_locations[0]
        query_image = query_image[top:bottom, left:right]
        query_encoding = face_recognition.face_encodings(query_image)[0]

        matches = face_recognition.compare_faces(encodings[person], query_encoding, tolerance=0.5)
        matches_count = matches.count(True)

        if i == j:
            if matches_count <= len(matches) // 2:
                print(f"{person} recognition is failed")
                true_negatives += 1
            else:
                print(f"{person} recognition passed")
                true_positives += 1
        else:
            if matches_count > len(matches) // 2:
                print(f"{j} th person seems like {person}")
                false_positives += 1


print(f"[INFO] total persons: {len(person)}")
print(f"[INFO] True negatives: {true_negatives}")
print(f"[INFO] True positive: {true_positives}")
print(f"[INFO] False positives: {false_positives}")
