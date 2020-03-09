import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from . import models as m


def jwt_payload_handler(user):
    payload = {
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(days=7)
    }

    return payload


def jwt_encode_handler(payload):
    key = settings.SECRET_KEY
    return jwt.encode(
        payload,
        key,
        algorithm='HS256'
    ).decode('utf-8')


class UserPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.UserPermission
        fields = '__all__'


class UserPermissionDetailSerializer(serializers.ModelSerializer):

    tree_data = serializers.SerializerMethodField()

    class Meta:
        model = m.UserPermission
        fields = (
            'id', 'name', 'description', 'tree_data'
        )

    def get_tree_data(self, instance):
        ret = []
        for permission in instance.permissions.all():
            action = permission.action
            for value in ret:
                if value['page'] == permission.page:
                    value['value'].append(action)
                    break
            else:
                ret.append({
                    'page': permission.page,
                    'value': [action],
                })

        return ret


class UserPermissionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.UserPermission
        exclude = (
            'permissions',
        )


class UserPermissionNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.UserPermission
        fields = (
            'id', 'name'
        )


class AuthSerializer(serializers.ModelSerializer):
    """
    Serializer for auth data of user
    """
    permissions = serializers.SerializerMethodField()
    # TODO: I think these fields need to be wrapped
    avatar = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = m.User
        fields = (
            'id', 'username', 'name', 'mobile', 'avatar', 'permissions', 'department'
        )

    def get_avatar(self, instance):
        try:
            profile = instance.profile
            request = self.context.get('request', None)
            avatar = profile.images.first()
            if avatar and request:
                avatar = request.build_absolute_uri(avatar.image.url)
            else:
                avatar = ''
        except ObjectDoesNotExist:
            avatar = ''

        return avatar

    def get_department(self, instance):
        try:
            profile = instance.profile
            department = profile.department.name
        except Exception:
            department = ''

        return department

    def get_permissions(self, instance):
        ret = []
        if instance.permission is not None:
            for permission in instance.permission.permissions.all():
                action = permission.action
                for value in ret:
                    if value['page'] == permission.page:
                        value['value'].append(action)
                        break
                else:
                    ret.append({
                        'page': permission.page,
                        'value': [action],
                    })

        return ret


class ObtainJWTSerializer(serializers.Serializer):
    """
    Serializer class used to validate a username and password.

    'username' is identified by the custom UserModel.USERNAME_FIELD.

    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        credentials = {
            'username': attrs.get('username'),
            'password': attrs.get('password'),
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg)
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg)


class VerificationBaseSerializer(serializers.Serializer):
    """
    Abstract serializer used for verifying and refreshing JWTs.
    """
    token = serializers.CharField()

    def validate(self, attrs):
        msg = 'Please define a validate method.'
        raise NotImplementedError(msg)

    def _check_payload(self, token):
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        options = {
            'verify_exp': False
        }
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, options=options)
        # except jwt.ExpiredSignature:
        #     msg = 'Signature has expired.'
        #     raise serializers.ValidationError(msg)
        except jwt.DecodeError:
            msg = 'Error decoding signature.'
            raise serializers.ValidationError(msg)

        return payload

    def _check_user(self, payload):
        username = payload.get('username')

        if not username:
            msg = 'Invalid payload.'
            raise serializers.ValidationError(msg)

        # Make sure user exists
        try:
            user = m.User.objects.get(username=username)
        except m.User.DoesNotExist:
            msg = "User doesn't exist."
            raise serializers.ValidationError(msg)

        if not user.is_active:
            msg = 'User account is disabled.'
            raise serializers.ValidationError(msg)

        return user


class VerifyJWTSerializer(VerificationBaseSerializer):
    """
    Check the veracity of an access token.
    """

    def validate(self, attrs):
        token = attrs['token']

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)

        return {
            'token': token,
            'user': user
        }


class UserNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.User
        fields = (
            'id', 'name'
        )


class ShortUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.User
        fields = (
            'id', 'username', 'name', 'mobile', 'permission'
        )


class UserSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField(required=False)

    class Meta:
        model = m.User
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = m.User(**validated_data)
        if password:
            user.set_password(password)

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

    def get_avatar(self, instance):
        try:
            profile = instance.profile
            request = self.context.get('request', None)
            avatar = profile.images.first()
            if avatar and request:
                avatar = request.build_absolute_uri(avatar.image.url)
            else:
                avatar = ''
        except ObjectDoesNotExist:
            avatar = ''

        return avatar
