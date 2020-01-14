from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer

from . import models as m
from . import serializers as s
from ..core.export import EXCEL_BODY_STYLE, EXCEL_HEAD_STYLE


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


class AttendanceTimeViewSet(XLSXFileMixin, viewsets.ModelViewSet):

    queryset = m.AttendanceTime.objects.all()
    serializer_class = s.AttendanceTimeSerializer
    body = EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = EXCEL_HEAD_STYLE
        ret['titles'] = [
            '部门', '考勤时间',

        ]
        return ret

    def get_queryset(self):
        queryset = self.queryset
        query_str = self.request.query_params.get('q', None)
        if query_str:
            queryset = queryset.filter(Q(name__icontains=query_str) | Q(description__icontains=query_str))

        sort_str = self.request.query_params.get('sort', None)
        if sort_str:
            queryset = queryset.order_by(sort_str)

        return queryset

    def create(self, request):
        context = {
            'slots': request.data.pop('slots', []),
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

    @action(detail=False, methods=['post'], url_path="bulk-delete")
    def bulk_delete(slef, request):
        m.AttendanceTime.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
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

    @action(detail=False, url_path="export", renderer_classes=[XLSXRenderer])
    def export(self, request):
        queryset = self.get_queryset()
        return Response(
            s.AttendanceTimeExportSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )
