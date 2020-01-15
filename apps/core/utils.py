import argparse
import cv2
import imutils
from imutils import paths


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", help="Path to Image dataset to be resized")
ap.add_argument("-w", "--width", type=int, default=150, help="Desired image width")

args = vars(ap.parse_args())

image_paths = list(paths.list_images(args["dataset"]))
for (i, image_path) in enumerate(image_paths):
    print(f"[INFO] processing {i} of {len(image_paths)} images...")
    image = cv2.imread(image_path)
    image = imutils.resize(image, width=args["width"])
    cv2.imwrite(image_path, image)
