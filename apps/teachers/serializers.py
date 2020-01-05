from rest_framework import serializers

from . import models as m
from ..accounts.serializers import UserNameSerializer
from ..core.serializers import Base64ImageField


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Department
        fields = '__all__'


class TeacherProfileSerializer(serializers.ModelSerializer):

    user = UserNameSerializer()

    class Meta:
        model = m.TeacherProfile
        fields = '__all__'


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
