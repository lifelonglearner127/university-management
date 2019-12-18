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
        exclude = (
            'id',
        )


class AttendanceTimeNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AttendanceTime
        fields = (
            'id', 'name',
        )


class AttendanceTimeSerializer(serializers.ModelSerializer):

    slots = TimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = m.AttendanceTime
        fields = '__all__'

    def create(self, validated_data):
        slots = self.context.pop('slots')
        instance = m.AttendanceTime.objects.create(**validated_data)

        for slot in slots:
            obj = m.TimeSlot.objects.create(**slot)
            instance.slots.add(obj)

        return instance

    def update(self, instance, validated_data):
        slots = self.context.pop('slots')
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        instance.slots.clear()
        for slot in slots:
            obj = m.TimeSlot.objects.create(**slot)
            instance.slots.add(obj)

        return instance
