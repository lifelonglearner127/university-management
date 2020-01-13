from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import serializers

from . import models as m
from ..accounts.serializers import UserNameSerializer, ShortUserSerializer
from ..core.serializers import Base64ImageField, TMSChoiceField


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Department
        fields = '__all__'


class DepartmentExportSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Department
        fields = (
            'name', 'description'
        )


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Position
        fields = '__all__'


class PositionExportSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Position
        fields = (
            'name', 'description'
        )


class TeacherImageSerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        model = m.TeacherImage
        fields = '__all__'


class TeacherImageOnlySerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        model = m.TeacherImage
        exclude = (
            'teacher',
        )


class TeacherImageSetSerializer(serializers.ModelSerializer):

    user = UserNameSerializer()
    images = TeacherImageOnlySerializer(many=True)

    class Meta:
        model = m.TeacherProfile
        fields = (
            'id', 'user', 'images',
        )


class TeacherProfileSerializer(serializers.ModelSerializer):

    user = ShortUserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    gender = TMSChoiceField(m.TeacherProfile.GENDER)
    images = TeacherImageOnlySerializer(many=True, read_only=True)

    class Meta:
        model = m.TeacherProfile
        fields = '__all__'

    def create(self, validated_data):
        user_data = self.context.pop('user', None)

        if not user_data:
            raise serializers.ValidationError("user data not provided")

        department = None
        department_data = self.context.pop('department', None)
        if department_data and department_data.get('id', None):
            department = get_object_or_404(m.Department, id=department_data.get('id'))

        position = None
        position_data = self.context.pop('position', None)
        if position_data and position_data.get('id', None):
            position = get_object_or_404(m.Position, id=position_data.get('id'))


        user_password = user_data.pop('password', None)
        user = m.User(**user_data)
        if user_password:
            user.set_password(user_password)
        user.save()

        return m.TeacherProfile.objects.create(
            user=user,
            department=department,
            position=position,
            **validated_data
        )

    def update(self, instance, validated_data):
        user_data = self.context.pop('user', None)

        if not user_data:
            raise serializers.ValidationError("user data not provided")

        instance.user.username = user_data["username"]
        instance.user.mobile = user_data["mobile"]

        user_password = user_data.pop('password', None)
        if user_password:
            instance.user.set_password(user_password)

        instance.user.save()

        department = None
        department_data = self.context.pop('department', None)
        if department_data and department_data.get('id', None):
            department = get_object_or_404(m.Department, id=department_data.get('id'))

        position = None
        position_data = self.context.pop('position', None)
        if position_data and position_data.get('id', None):
            position = get_object_or_404(m.Position, id=position_data.get('id'))

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.department = department
        instance.position = position
        instance.save()

        return instance


class TeacherProfileExportSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='user.name')
    work_no = serializers.CharField()
    username = serializers.CharField(source='user.username')
    department = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    gender = serializers.CharField(source='get_gender_display')
    mobile = serializers.CharField(source='user.mobile')

    class Meta:
        model = m.TeacherProfile
        fields = (
            'name', 'work_no', 'username', 'department', 'position', 'gender', 'mobile',
        )

    def get_department(self, instance):
        return instance.department.name if instance.department else ''

    def get_position(self, instance):
        return instance.position.name if instance.position else ''
