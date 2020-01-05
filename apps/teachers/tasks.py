import os
import pickle
import face_recognition
from config.celery import app
from django.conf import settings
from django.shortcuts import get_object_or_404
from . import models as m


@app.task
def extract_feature(context):
    teacher_id = context['teacher']
    teacher = get_object_or_404(m.Teacher, id=teacher_id)
    username = teacher.user.username

    image_paths = teacher.images.values_list('image', flat=True)
    encodings = []
    for image_path in image_paths:
        image = face_recognition.load_image_file(os.path.join(settings.MEDIA_ROOT, image_path))
        encodings.append(face_recognition.face_encodings(image)[0])

    if not os.path.exists(settings.FEATURE_ROOT):
        os.makedirs(settings.FEATURE_ROOT)

    file_name = os.path.join(settings.FEATURE_ROOT, f"{username}.pickle")
    with open(file_name, "wb+") as f:
        f.write(pickle.dumps(encodings))
