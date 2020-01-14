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

    open_time = serializers.TimeField(format="%H:%M")
    start_open_time = serializers.TimeField(format="%H:%M")
    finish_open_time = serializers.TimeField(format="%H:%M")
    close_time = serializers.TimeField(format="%H:%M")
    start_close_time = serializers.TimeField(format="%H:%M")
    finish_close_time = serializers.TimeField(format="%H:%M")

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


class AttendanceTimeExportSerializer(serializers.ModelSerializer):

    slots = serializers.SerializerMethodField()

    class Meta:
        model = m.AttendanceTime
        fields = (
            'name', 'slots'
        )

    def get_slots(self, instance):
        ret = []
        for slot in instance.slots.all():
            ret.append(slot.start_open_time.strftime('%H:%M') + '-' + slot.finish_open_time.strftime('%H:%M'))
            ret.append(slot.start_close_time.strftime('%H:%M') + '-' + slot.finish_close_time.strftime('%H:%M'))

        return ', '.join(ret)
