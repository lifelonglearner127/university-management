from rest_framework import serializers

from . import models as m


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Department
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Profile
        fields = '__all__'
