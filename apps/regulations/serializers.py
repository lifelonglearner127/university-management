from itertools import islice
from rest_framework import serializers

from . import models as m
from ..teachers.serializers import ShortTeacherProfileSerializer


batch_size = 100


class AttendancePlaceNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AttendancePlace
        fields = (
            'id', 'name',
        )


class AttendancePlaceExportSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AttendancePlace
        fields = (
            'name', 'address', 'longitude', 'latitude', 'radius'
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


class AttendanceRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AttendanceRule
        fields = '__all__'

    def create(self, validated_data):
        attendees = self.context.get('attendees', [])
        nonattendees = self.context.get('nonattendees', [])
        events = self.context.get('events', [])

        attendance_rule = m.AttendanceRule.objects.create(**validated_data)

        # create attendees
        attendees = m.TeacherProfile.objects.filter(id__in=attendees)
        objs = (m.AttendanceMembership(teacher=teacher, rule=attendance_rule) for teacher in attendees)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.AttendanceMembership.objects.bulk_create(batch, batch_size)

        # create nonattendees
        nonattendees = m.TeacherProfile.objects.filter(id__in=nonattendees)
        objs = (m.UnAttendenceMembership(teacher=teacher, rule=attendance_rule) for teacher in nonattendees)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.UnAttendenceMembership.objects.bulk_create(batch, batch_size)

        # create events
        objs = (m.AttendanceEvent(rule=attendance_rule, is_attendance_day=event['is_attendance_day'],
                                 start_date=event['start_date'], end_date=event['end_date'],
                                 description=event['description'])
                for event in events)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.AttendanceEvent.objects.bulk_create(batch, batch_size)
        return attendance_rule

    def update(self, instance, validated_data):
        attendees = self.context.get('attendees', [])
        nonattendees = self.context.get('nonattendees', [])
        events = self.context.get('events', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        # update attendees
        old_attendees_ids = set(instance.attendees.values_list('id', flat=True))
        new_attendees_ids = set(attendees)
        m.AttendanceMembership.objects.filter(
            rule=instance, teacher__id__in=old_attendees_ids.difference(new_attendees_ids)
        ).delete()

        new_attendees = m.TeacherProfile.objects.filter(id__in=new_attendees_ids.difference(old_attendees_ids))
        objs = (m.AttendanceMembership(rule=instance, teacher=teacher) for teacher in new_attendees)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.AttendanceMembership.objects.bulk_create(batch, batch_size)

        # update nonattendees
        old_non_attendees_ids = set(instance.nonattendees.values_list('id', flat=True))
        new_non_attendees_ids = set(nonattendees)
        m.UnAttendenceMembership.objects.filter(
            rule=instance, teacher__id__in=old_non_attendees_ids.difference(new_non_attendees_ids)
        ).delete()

        new_non_attendees = m.TeacherProfile.objects.filter(
            id__in=new_non_attendees_ids.difference(old_non_attendees_ids)
        )
        objs = (m.UnAttendenceMembership(rule=instance, teacher=teacher) for teacher in new_non_attendees)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.UnAttendenceMembership.objects.bulk_create(batch, batch_size)

        # update events
        old_event_ids = set(m.AttendanceEvent.objects.filter(rule=instance).values_list('id', flat=True))
        new_event_ids = set([event['id'] for event in events])
        m.AttendanceEvent.objects.filter(id__in=old_event_ids.difference(new_event_ids)).delete()

        new_events = [event for event in events if str(event['id']).startswith('new')]
        objs = (m.AttendanceEvent(rule=instance, is_attendance_day=event['is_attendance_day'],
                                  start_date=event['start_date'], end_date=event['end_date'],
                                  description=event['description'])
                for event in new_events)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.AttendanceEvent.objects.bulk_create(batch, batch_size)

        return instance


class AttendanceRuleListSerializer(serializers.ModelSerializer):

    attendance_place = AttendancePlaceNameSerializer()
    attendees_num = serializers.IntegerField()
    nonattendees_num = serializers.IntegerField()

    class Meta:
        model = m.AttendanceRule
        fields = (
            'id', 'name', 'attendance_place', 'attendees_num', 'nonattendees_num'
        )


class AttendanceWeekField(serializers.Field):
    def to_representation(self, instance):
        ret = []
        week = {
            '一': instance.mon,
            '二': instance.tue,
            '三': instance.wed,
            '四': instance.thr,
            '五': instance.fri,
            '六': instance.sat,
            '日': instance.sun
        }

        identifier = 0
        for day, attendance_time in week.items():
            if attendance_time:
                is_checked = True
                attendance_time = AttendanceTimeSerializer(attendance_time).data
            else:
                is_checked = False
                attendance_time = None

            ret.append(
                {
                    'id': identifier,
                    'day': day,
                    'is_checked': is_checked,
                    'attendance_time': attendance_time
                }
            )
            identifier += 1

        return ret


class AttendanceEventSerializer(serializers.ModelSerializer):

    start_date = serializers.DateField(
        format='%Y-%m-%d', required=False
    )
    end_date = serializers.DateField(
        format='%Y-%m-%d', required=False
    )

    class Meta:
        model = m.AttendanceEvent
        exclude = (
            'rule',
        )


class AttendanceRuleDetailSerializer(serializers.ModelSerializer):

    week = AttendanceWeekField(source='*')
    attendees = ShortTeacherProfileSerializer(many=True)
    nonattendees = ShortTeacherProfileSerializer(many=True)
    events = serializers.SerializerMethodField()
    attendance_place = AttendancePlaceNameSerializer()

    class Meta:
        model = m.AttendanceRule
        fields = (
            'id', 'name', 'attendees', 'nonattendees', 'attendance_place', 'week', 'events'
        )

    def get_events(self, instance):
        events = m.AttendanceEvent.objects.filter(rule=instance)
        return AttendanceEventSerializer(events, many=True).data
