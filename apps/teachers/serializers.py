from rest_framework import serializers

from . import models as m


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Department
        fields = '__all__'


class TeacherProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.TeacherProfile
        fields = '__all__'
