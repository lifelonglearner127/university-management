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
