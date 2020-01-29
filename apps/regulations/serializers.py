import os

import face_recognition
import numpy as np
from datetime import date, datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from geopy import distance
from itertools import islice
from rest_framework import serializers

from . import models as m
from . import exceptions as e
from .helpers import get_week_day
from ..teachers.serializers import ShortTeacherProfileSerializer
from ..core.serializers import Base64ImageField


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


class ShortTimeSlotSerializer(serializers.ModelSerializer):

    open_time = serializers.TimeField(format="%H:%M")
    close_time = serializers.TimeField(format="%H:%M")

    class Meta:
        model = m.TimeSlot
        fields = (
            'open_time', 'close_time'
        )


class TimeSlotOpenTimeSerializer(serializers.ModelSerializer):

    rule_time = serializers.TimeField(format="%H:%M", source='open_time')

    class Meta:
        model = m.TimeSlot
        fields = (
            'id', 'rule_time'
        )


class TimeSlotCloseTimeSerializer(serializers.ModelSerializer):

    rule_time = serializers.TimeField(format="%H:%M", source='close_time')

    class Meta:
        model = m.TimeSlot
        fields = (
            'id', 'rule_time'
        )


class TimeSlotSerializer(serializers.ModelSerializer):

    open_time = serializers.TimeField(format="%H:%M")
    start_open_time = serializers.TimeField(format="%H:%M")
    finish_open_time = serializers.TimeField(format="%H:%M")
    close_time = serializers.TimeField(format="%H:%M")
    start_close_time = serializers.TimeField(format="%H:%M")
    finish_close_time = serializers.TimeField(format="%H:%M")

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

        old_slot_ids = set(instance.slots.values_list('id', flat=True))
        new_slot_ids = set({})
        # instance.slots.clear()
        for slot_data in slots:
            slot_id = slot_data.get('id', None)
            if slot_id:
                new_slot_ids.add(slot_id)
                slot = get_object_or_404(m.TimeSlot, id=slot_id)
                for key, value in slot_data.items():
                    setattr(slot, key, value)

                slot.save()
            else:
                obj = m.TimeSlot.objects.create(**slot_data)
                instance.slots.add(obj)

        instance.slots.filter(
            id__in=old_slot_ids.difference(new_slot_ids)
        ).delete()

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
        objs = (m.UnAttendanceMembership(teacher=teacher, rule=attendance_rule) for teacher in nonattendees)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.UnAttendanceMembership.objects.bulk_create(batch, batch_size)

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
        m.UnAttendanceMembership.objects.filter(
            rule=instance, teacher__id__in=old_non_attendees_ids.difference(new_non_attendees_ids)
        ).delete()

        new_non_attendees = m.TeacherProfile.objects.filter(
            id__in=new_non_attendees_ids.difference(old_non_attendees_ids)
        )
        objs = (m.UnAttendanceMembership(rule=instance, teacher=teacher) for teacher in new_non_attendees)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.UnAttendanceMembership.objects.bulk_create(batch, batch_size)

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


class AttendanceHistorySerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        model = m.AttendanceHistory
        fields = '__all__'


class AttendSerializer(serializers.ModelSerializer):

    image = Base64ImageField()
    identified_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = m.AttendanceHistory
        fields = '__all__'

    def create(self, validated_data):
        attendance_place = validated_data['membership'].rule.attendance_place
        if attendance_place:
            distance_delta = distance.distance((attendance_place.latitude, attendance_place.longitude),
                                               (validated_data['latitude'], validated_data['longitude'])).m
            if distance_delta > attendance_place.radius:
                validated_data['is_right_place'] = False

        return m.AttendanceHistory.objects.create(**validated_data)

    def validate(self, data):
        # Rule validations
        today = date.today()
        membership = data['membership']
        time_slot = data['time_slot']
        if membership.rule.events.filter(
            is_attendance_day=False, start_date__gte=today, end_date__lte=today
        ).exists():
            raise e.NO_ATTENDANCE_DAY

        # check day attendance rule
        day_rule = get_week_day(membership.rule, today.weekday())
        if not day_rule:
            raise e.NO_ATTENDANCE_DAY

        # check whether day rule has time slots
        if time_slot not in day_rule.slots.all():
            raise e.TIMESLOT_MISSING

        # check whether it is in range of attendable time
        current_time = datetime.now().time()

        if data['is_open_attend']:
            attendance_time = time_slot.open_time
            attendance_start_time = time_slot.start_open_time
            attendance_end_time = time_slot.finish_open_time
        else:
            attendance_time = time_slot.close_time
            attendance_start_time = time_slot.start_close_time
            attendance_end_time = time_slot.finish_close_time

        if current_time < attendance_start_time or current_time > attendance_end_time:
            raise e.OUT_OF_ATTENDANCE_TIME

        if (current_time > attendance_time and data['is_open_attend']) or\
           (current_time < attendance_time and not data['is_open_attend']):
            data['is_bad_attendance'] = True

        # TODO OR NOT: Right now I am not sure whether this validation is needed or no.
        # Filtering duplicate attendance request

        # face validations
        query_image = face_recognition.load_image_file(data['image'])
        query_encoding = face_recognition.face_encodings(query_image)[0]
        user = self.context.get('user')
        username = user.username
        file_name = os.path.join(settings.FEATURE_ROOT, f"{username}.txt")
        if not os.path.exists(file_name):
            raise e.FACE_RECOGNITION_NO_DATASET('No dataset')

        encodings = np.loadtxt(file_name)
        matches = face_recognition.compare_faces(encodings, query_encoding)
        matches_count = matches.count(True)
        if matches_count < int(len(matches) * 0.2):
            raise e.FACE_RECOGNITION_FAILED('Failed recognition')

        return data


class AttendanceDailyReportSerializer(serializers.Serializer):

    attendance_rule_id = serializers.IntegerField()
    attendance_time_id = serializers.IntegerField()
    attendance_date = serializers.DateField(format='%Y-%m-%d')
    is_open_attend = serializers.BooleanField()
    attendance_time = serializers.TimeField(format="%H:%M")
    total_member_num = serializers.IntegerField()
    attendees_num = serializers.IntegerField()
    late_attendees_num = serializers.IntegerField()
    early_departures_num = serializers.IntegerField()
    absentees_num = serializers.IntegerField()
    outside_area_num = serializers.IntegerField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = ret['attendance_date'] + str(ret['attendance_time_id'])
        return ret


class AttendanceDailyReportDetailSerializer(serializers.Serializer):

    attendance_date = serializers.DateField(format='%Y-%m-%d')
    attendance_place = serializers.CharField()
    attendance_dow = serializers.IntegerField()
    attendance_time = serializers.TimeField(format="%H:%M")
    attendance_start_time = serializers.TimeField(format="%H:%M")
    attendance_end_time = serializers.TimeField(format="%H:%M")
    total_member_num = serializers.IntegerField()
    attendees_num = serializers.IntegerField()
    bad_attendees_num = serializers.IntegerField()
    absentees_num = serializers.IntegerField()
    outside_area_num = serializers.IntegerField()


class AttendanceDailyReportExportSerializer(serializers.Serializer):

    attendance_date = serializers.DateField(format='%Y-%m-%d')
    attendance_time = serializers.TimeField(format="%H:%M")
    total_member_num = serializers.IntegerField()
    attendees_num = serializers.IntegerField()
    late_attendees_num = serializers.IntegerField()
    early_departures_num = serializers.IntegerField()
    absentees_num = serializers.IntegerField()
    outside_area_num = serializers.IntegerField()


class AttendeesReportSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    work_no = serializers.CharField()
    name = serializers.CharField()
    department = serializers.CharField()
    work_days = serializers.IntegerField()
    late_attendance_days = serializers.IntegerField()
    early_departure_days = serializers.IntegerField()
    unchecked_days = serializers.IntegerField()
    outside_area_days = serializers.IntegerField()


class AttendeesReportExportSerializer(AttendeesReportSerializer):

    id = None


class AttendanceDailyHistorySerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField(source='user__name')
    identified_on = serializers.DateTimeField(format='%H:%M:%S')
    image = serializers.CharField()
    is_right_place = serializers.BooleanField()
    is_bad_attendance = serializers.BooleanField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request', None)
        if ret['image'] and request:
            ret['image'] = request.build_absolute_uri(settings.MEDIA_URL + ret['image'])

        return ret
