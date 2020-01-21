import base64
import io
import os
import pickle
import six
import face_recognition
from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer

from . import models as m
from . import serializers as s
from ..core.export import EXCEL_BODY_STYLE, EXCEL_HEAD_STYLE
from .tasks import extract_feature


class DepartmentViewSet(XLSXFileMixin, viewsets.ModelViewSet):

    queryset = m.Department.objects.all()
    serializer_class = s.DepartmentSerializer
    body = EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = EXCEL_HEAD_STYLE
        ret['titles'] = [
            '部门', '备注',

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

    @action(detail=False, methods=['post'], url_path="bulk-delete")
    def bulk_delete(slef, request):
        m.Department.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="all")
    def get_all_departments(self, request):
        return Response(
            self.serializer_class(m.Department.objects.all(), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="export", renderer_classes=[XLSXRenderer])
    def export(self, request):
        queryset = self.get_queryset()
        return Response(
            s.DepartmentExportSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )


class PositionViewSet(XLSXFileMixin, viewsets.ModelViewSet):

    queryset = m.Position.objects.all()
    serializer_class = s.PositionSerializer
    body = EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = EXCEL_HEAD_STYLE
        ret['titles'] = [
            '职位', '备注',

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

    @action(detail=False, methods=['post'], url_path="bulk-delete")
    def bulk_delete(slef, request):
        m.Position.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="all")
    def get_all_positions(self, request):
        return Response(
            self.serializer_class(m.Position.objects.all(), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="export", renderer_classes=[XLSXRenderer])
    def export(self, request):
        queryset = self.get_queryset()
        return Response(
            s.PositionExportSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )


class TeacherViewSet(XLSXFileMixin, viewsets.ModelViewSet):

    queryset = m.TeacherProfile.objects.all()
    serializer_class = s.TeacherProfileSerializer
    body = EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = EXCEL_HEAD_STYLE
        ret['titles'] = [
            '名称', '工号', '登录名', '部门', '职位', '性别', '联系电话'
        ]
        return ret

    def get_queryset(self):
        queryset = self.queryset
        query_str = self.request.query_params.get('q', None)
        if query_str:
            queryset = queryset.filter(Q(user__name__icontains=query_str) | Q(work_no=query_str))

        department_query = self.request.query_params.get('departments', None)
        if department_query:
            departments = department_query.split(',')
            queryset = queryset.filter(department__id__in=departments)

        sort_str = self.request.query_params.get('sort', None)
        if sort_str:
            queryset = queryset.order_by(sort_str)

        return queryset

    def create(self, request):
        user_data = request.data.pop('user', None)
        context = {
            'user': user_data,
            'department': request.data.pop('department', None),
            'position': request.data.pop('position', None),
            'permission': request.data.pop('permission', None)
        }

        if user_data:
            query_filter = Q(username=user_data["username"]) | Q(mobile=user_data["mobile"])
            if m.User.objects.filter(query_filter).exists():
                return Response(
                    {
                        'code': -1,
                        'msg': 'Duplicate username or mobile'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = s.TeacherProfileSerializer(
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()

        user_data = request.data.pop('user', None)

        context = {
            'user': user_data,
            'department': request.data.pop('department', None),
            'position': request.data.pop('position', None),
            'permission': request.data.pop('permission', None)
        }

        query_filter = Q(username=user_data["username"]) | Q(mobile=user_data["mobile"])
        if m.User.objects.exclude(id=instance.user.id).filter(query_filter).exists():
            return Response(
                    {
                        'code': -1,
                        'msg': 'Duplicate username or mobile'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = s.TeacherProfileSerializer(
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

    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.user.delete()

        return Response(
            {
                "msg": "Deleted Successfully"
            },
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, url_path='short')
    def get_short_profiles(self, request):
        page = self.paginate_queryset(self.get_queryset())
        serializer = s.ShortTeacherProfileSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post'], url_path='id-restriction/short')
    def get_short_profiles_with_id_restriction(self, request):
        queryset = self.queryset
        query_str = request.data.get('q', None)
        if query_str:
            queryset = queryset.filter(Q(user__name__icontains=query_str) | Q(work_no=query_str))

        departments = request.data.get('departments', [])
        if departments:
            queryset = queryset.filter(department__id__in=departments)

        ids = request.data.get('ids', [])
        queryset = queryset.filter(~Q(id__in=ids))

        sort_str = request.data.get('sort', None)
        if sort_str:
            queryset = queryset.order_by(sort_str)

        page = self.paginate_queryset(queryset)
        serializer = s.ShortTeacherProfileSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post'], url_path="bulk-delete")
    def bulk_delete(self, request):
        user_ids = m.TeacherProfile.objects.filter(
            id__in=request.data.get('ids', [])
        ).values_list('user__id', flat=True)
        m.User.objects.filter(id__in=user_ids).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        instance = self.get_object()
        instance.user.set_password(request.data.pop('password', ''))
        instance.user.save()
        return Response(
            {
                'msg': 'Password reset successfully'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="export", renderer_classes=[XLSXRenderer])
    def export(self, request):
        queryset = self.get_queryset()
        return Response(
            s.TeacherProfileExportSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path="delete-image")
    def delete_image(self, request, pk=None):
        instance = self.get_object()
        image_id = request.data.get('id', None)
        if image_id:
            instance.images.filter(id=image_id).delete()

        return Response(
            self.serializer_class(
                instance,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path="delete-images")
    def delete_images(self, request, pk=None):
        instance = self.get_object()
        image_ids = request.data.get('ids', [])
        if image_ids:
            instance.images.filter(id__in=image_ids).delete()

        return Response(
            self.serializer_class(
                instance,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path="delete-image")
    def delete_my_image(self, request, pk=None):
        instance = self.get_object()
        image_id = request.data.get('id', None)
        if image_id:
            instance.images.filter(id=image_id).delete()

        return Response(
            self.serializer_class(
                instance,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser], url_path="upload-images")
    def upload_images(self, request, pk=None):
        instance = self.get_object()
        for _, image in request.data.items():
            serializer = s.TeacherImageSerializer(
                data={
                    "teacher": instance.id,
                    "image": image
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        extract_feature.apply_async(
            args=[{
                'teacher': instance.id
            }]
        )
        return Response(
            s.TeacherImageSetSerializer(instance, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path="me/upload-images")
    def upload_my_images(self, request):
        my_profile = request.user.profile
        images = request.data.pop('files', [])
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
