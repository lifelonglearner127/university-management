from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s


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
                },
                context={
                    'request': request
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(
            s.TeacherImageSetSerializer(my_profile).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="me/get-images")
    def get_my_images(self, request):
        my_profile = request.user.profile
        return Response(
            s.TeacherImageSetSerializer(my_profile, context={'request': request}).data,
            status=status.HTTP_200_OK
        )
