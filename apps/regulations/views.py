from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s


class AttendancePlaceViewSet(viewsets.ModelViewSet):

    queryset = m.AttendancePlace.objects.all()
    serializer_class = s.AttendancePlaceSerializer

    @action(detail=False, url_path="all")
    def get_all_places(self, request):
        return Response(
            self.serializer_class(self.queryset, many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="all/names")
    def get_all_places_names(self, request):
        return Response(
            s.AttendancePlaceNameSerializer(self.queryset, many=True).data,
            status=status.HTTP_200_OK
        )


class AttendanceTimeViewSet(viewsets.ModelViewSet):

    queryset = m.AttendanceTime.objects.all()
    serializer_class = s.AttendanceTimeSerializer

    def create(self, request):
        context = {
            'slots': request.data.pop('slots'),
        }

        serializer = self.serializer_class(
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        context = {
            'slots': request.data.pop('slots'),
        }

        serializer = self.serializer_class(
            instance,
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="all")
    def get_all_times(self, request):
        return Response(
            self.serializer_class(self.queryset, many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="all/names")
    def get_all_times_names(self, request):
        return Response(
            s.AttendanceTimeNameSerializer(self.queryset, many=True).data,
            status=status.HTTP_200_OK
        )
