import base64
import io
import os
import pickle
import six
import face_recognition
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from .tasks import extract_feature


class DepartmentViewSet(viewsets.ModelViewSet):

    queryset = m.Department.objects.all()
    serializer_class = s.DepartmentSerializer

    @action(detail=False, url_path="all")
    def get_all_departments(self, request):
        return Response(
            self.serializer_class(self.queryset, many=True).data,
            status=status.HTTP_200_OK
        )


class TeacherViewSet(viewsets.ModelViewSet):

    queryset = m.Teacher.objects.all()
    serializer_class = s.TeacherSerializer

    @action(detail=False, methods=['post'], url_path="me/upload-images")
    def upload_my_images(self, request):
        my_profile = request.user.profile
        images = request.data.pop('images', [])
        for image in images:
            serializer = s.TeacherImageSerializer(
                data={
                    "teacher": my_profile.id,
                    "image": image["image"]
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        extract_feature.apply_async(
            args=[{
                'teacher': my_profile.id
            }]
        )
        return Response(
            s.TeacherImageSetSerializer(my_profile, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="me/get-images")
    def get_my_images(self, request):
        my_profile = request.user.profile
        return Response(
            s.TeacherImageSetSerializer(my_profile, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path="me/identify-face")
    def identify_face(self, request):
        query_image = request.data.pop('image', None)
        if query_image is None or not isinstance(query_image, six.string_types) or\
           not query_image.startswith('data:image'):
            return Response(
                {
                    "code": -1,
                    "msg": "Error request body"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        header, query_image = query_image.split(';base64,')

        try:
            query_image = base64.b64decode(query_image)
        except TypeError:
            return Response(
                {
                    "code": -1,
                    "msg": "Error request body"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:

            query_image = face_recognition.load_image_file(io.BytesIO(query_image))
            query_encoding = face_recognition.face_encodings(query_image)[0]

            username = request.user.username
            file_name = os.path.join(settings.FEATURE_ROOT, f"{username}.pickle")
            if not os.path.exists(file_name):
                return Response(
                    {
                        "code": -1,
                        "msg": "You cannot identify your face right now"
                    },
                    status=status.HTTP_200_OK
                )

            encodings = pickle.loads(open(file_name, "rb").read())
            matches = face_recognition.compare_faces(encodings, query_encoding)
            matches_count = matches.count(True)
            if matches_count > int(len(matches) * 0.8):
                return Response(
                    {
                        "code": 0,
                        "result": True
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "code": -1,
                        "result": False
                    },
                    status=status.HTTP_200_OK
                )
