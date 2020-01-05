from django.db.models import Q
from rest_framework import serializers

from . import models as m
from ..accounts.serializers import UserNameSerializer, ShortUserSerializer
from ..core.serializers import Base64ImageField, TMSChoiceField


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Department
        fields = '__all__'


class TeacherProfileSerializer(serializers.ModelSerializer):

    user = ShortUserSerializer(read_only=True)
    gender = TMSChoiceField(m.TeacherProfile.GENDER)

    class Meta:
        model = m.TeacherProfile
        fields = '__all__'

    def create(self, validated_data):
        user_data = self.context.pop('user', None)

        if not user_data:
            raise serializers.ValidationError("user data not provided")

        query_filter = Q(username=user_data["username"]) | Q(mobile=user_data["mobile"])

        if m.User.objects.filter(query_filter).exists():
            raise serializers.ValidationError("Duplicate username or mobile")

        user_password = user_data.pop('password', None)
        user = m.User(**user_data)
        if user_password:
            user.set_password(user_password)
        user.save()

        return m.TeacherProfile.objects.create(
            user=user,
            **validated_data
        )

    def update(self, instance, validated_data):
        user_data = self.context.pop('user', None)

        if not user_data:
            raise serializers.ValidationError("user data not provided")

        query_filter = Q(username=user_data["username"]) | Q(mobile=user_data["mobile"])
        if m.User.objects.exclude(id=instance.user.id).filter(query_filter).exists():
            raise serializers.ValidationError("Duplicate username or mobile")

        instance.user.username = user_data["username"]
        instance.user.mobile = user_data["mobile"]

        user_password = user_data.pop('password', None)
        if user_password:
            instance.user.set_password(user_password)

        instance.user.save()

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


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
