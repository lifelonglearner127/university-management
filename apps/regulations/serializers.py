from rest_framework import serializers

from . import models as m


class AttendancePlaceNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AttendancePlace
        fields = (
            'id', 'name',
        )


class AttendancePlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AttendancePlace
        fields = '__all__'


class TimeSlotSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.TimeSlot
        fields = '__all__'


class AttendanceTimeNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AttendanceTime
        fields = (
            'id', 'name',
        )


class AttendanceTimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AttendanceTime
        fields = '__all__'

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
