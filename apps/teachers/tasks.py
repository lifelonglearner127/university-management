import os
import face_recognition
import numpy as np
from config.celery import app
from django.conf import settings
from django.shortcuts import get_object_or_404
from . import models as m


@app.task
def extract_feature(context):
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
