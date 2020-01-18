from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from . import serializers as s
from . import models as m


class JWTAPIView(APIView):
    """
    Base API View that various JWT interactions inherit from.
    """
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data.get('user') or request.user
            token = serializer.validated_data.get('token')

            return Response({
                'token': token,
                'user': s.AuthSerializer(
                    user,
                    context={
                        'request': request
                    }
                ).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainJWTAPIView(JWTAPIView):
    """
    API View that receives a POST with username and password and user user_type
    Returns a JSON Web Token with user data
    """
    serializer_class = s.ObtainJWTSerializer


class VerifyJWTAPIView(JWTAPIView):
    """
    API View that checks the veracity of a token, returning the token and
    user data if it is valid.
    """
    serializer_class = s.VerifyJWTSerializer


class UserViewSet(viewsets.ModelViewSet):

    queryset = m.User.objects.all()
    serializer_class = s.UserSerializer

    @action(detail=False, url_path='names/all')
    def get_all_names(self, request):
        return Response(
            s.UserNameSerializer(m.User.objects.all(), many=True).data,
            status=status.HTTP_200_OK
        )


class UserPermissionViewSet(viewsets.ModelViewSet):

    queryset = m.UserPermission.objects.all()
    serializer_class = s.UserPermissionSerializer

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
        data = request.data
        permission_data = request.data.pop('permissions')
        permissions = []
        for key, actions in permission_data.items():
            for action_name in actions:
                obj, created = m.Permission.objects.get_or_create(
                    page=key,
                    action=action_name
                )
                permissions.append(obj.id)

        data['permissions'] = permissions
        serializer = s.UserPermissionSerializer(
            data=data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = self.get_object()
        data = request.data
        permission_data = request.data.pop('permissions')
        permissions = []
        for key, actions in permission_data.items():
            for action_name in actions:
                obj, created = m.Permission.objects.get_or_create(
                    page=key,
                    action=action_name
                )
                permissions.append(obj.id)

        data['permissions'] = permissions
        serializer = s.UserPermissionSerializer(
            instance, data=data, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        page = self.paginate_queryset(self.get_queryset())
        serializer = s.UserPermissionListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(m.UserPermission, id=pk)
        serializer = s.UserPermissionDetailSerializer(instance)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='names/all')
    def get_all_names(self, request):
        return Response(
            s.UserPermissionNameSerializer(m.UserPermission.objects.all(), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path="bulk-delete")
    def bulk_delete(slef, request):
        m.UserPermission.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
            status=status.HTTP_200_OK
        )
