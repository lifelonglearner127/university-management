from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from . import serializers as s
from . import models as m
from ..teachers.models import TeacherProfile


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
            name = user.name if user.name else user.username
            avatar = None

            try:
                teacher = TeacherProfile.objects.get(user=user)
                avatar = teacher.images.first()
                if avatar:
                    avatar = request.build_absolute_uri(avatar.image.url)

            except TeacherProfile.DoesNotExist:
                pass

            return Response({
                'token': token,
                'user': s.AuthSerializer({
                    'id': user.id,
                    'username': user.username,
                    'name': name,
                    'avatar': avatar
                }).data
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
