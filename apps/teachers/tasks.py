import os
import cv2
import face_recognition
import numpy as np
from config.celery import app
from django.conf import settings
from django.shortcuts import get_object_or_404
from . import models as m


@app.task
def extract_feature(context):
    """
    Append the 128d-features to the encoding files once images are added
    This is not used for now. Older version
    """
    teacher_id = context['teacher']
    image_ids = context['image_ids']
    teacher = get_object_or_404(m.TeacherProfile, id=teacher_id)
    username = teacher.user.username

    if not os.path.exists(settings.FEATURE_ROOT):
        os.makedirs(settings.FEATURE_ROOT)

    image_paths = teacher.images.filter(id__in=image_ids).values_list('image', flat=True)

    encodings = []
    for image_path in image_paths:
        image = face_recognition.load_image_file(os.path.join(settings.MEDIA_ROOT, image_path))
       encodings.append(face_recognition.face_encodings(image)[0])

    file_name = os.path.join(settings.FEATURE_ROOT, f"{username}.txt")
    with open(file_name, "ab") as f:
        np.savetxt(f, encodings)


@app.task
def sync_extract_feature(context):
    """
    Reconstruct the encoding files
    """
    teacher_id = context['teacher']
    teacher = get_object_or_404(m.TeacherProfile, id=teacher_id)
    username = teacher.user.username

    if not os.path.exists(settings.FEATURE_ROOT):
        os.makedirs(settings.FEATURE_ROOT)

    image_paths = teacher.images.values_list('image', flat=True)

    encodings = []
    for image_path in image_paths:
        image_server_path = os.path.join(settings.MEDIA_ROOT, image_path)
        image = cv2.imread(image_server_path)
        (top, right, bottom, left) = face_recognition.face_locations(image)[0]
        detected_face = image[top:bottom, left:right]
        cv2.imwrite(image_server_path, detected_face)
        encodings.append(face_recognition.face_encodings(detected_face)[0])

    file_name = os.path.join(settings.FEATURE_ROOT, f"{username}.txt")
    with open(file_name, "wb") as f:
        np.savetxt(f, encodings)
