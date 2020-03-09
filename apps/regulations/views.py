import time
from datetime import date, datetime, timedelta
from django.db.models import F, Q, Count, Case, When, OuterRef, Subquery, ExpressionWrapper, BooleanField
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer

from . import models as m
from . import serializers as s
from . import exceptions as e
from .helpers import get_week_day
from ..core.export import EXCEL_BODY_STYLE, EXCEL_HEAD_STYLE


class AttendancePlaceViewSet(XLSXFileMixin, viewsets.ModelViewSet):

    queryset = m.AttendancePlace.objects.all()
    serializer_class = s.AttendancePlaceSerializer
    body = EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = EXCEL_HEAD_STYLE
        ret['titles'] = [
            '部门', '考勤时间',

        ]
        return ret

    def get_queryset(self):
        queryset = self.queryset
        query_str = self.request.query_params.get('q', None)
        if query_str:
            queryset = queryset.filter(Q(name__icontains=query_str))

        sort_str = self.request.query_params.get('sort', None)
        if sort_str:
            queryset = queryset.order_by(sort_str)

        return queryset

    @action(detail=False, url_path="all")
    def get_all_places(self, request):
        return Response(
            self.serializer_class(m.AttendancePlace.objects.all(), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="all/names")
    def get_all_places_names(self, request):
        return Response(
            s.AttendancePlaceNameSerializer(m.AttendancePlace.objects.all(), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path="bulk-delete")
    def bulk_delete(slef, request):
        m.AttendancePlace.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="export", renderer_classes=[XLSXRenderer])
    def export(self, request):
        queryset = self.get_queryset()
        return Response(
            s.AttendancePlaceExportSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )


class AttendanceTimeViewSet(XLSXFileMixin, viewsets.ModelViewSet):

    queryset = m.AttendanceTime.objects.all()
    serializer_class = s.AttendanceTimeSerializer
    body = EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = EXCEL_HEAD_STYLE
        ret['titles'] = [
            '部门', '考勤时间',

        ]
        return ret

    def get_queryset(self):
        queryset = self.queryset
        query_str = self.request.query_params.get('q', None)
        if query_str:
            queryset = queryset.filter(Q(name__icontains=query_str) | Q(description__icontains=query_str))

        sort_str = self.request.query_params.get('sort', None)
        if sort_str:
            queryset = queryset.order_by(sort_str)

        return queryset

    def create(self, request):
        time_slots = request.data.pop('slots', [])
        context = {
            'slots': time_slots,
        }

        for time_slot in time_slots:
            open_time = time.strptime(time_slot["open_time"], '%H:%M')
            start_open_time = time.strptime(time_slot["start_open_time"], '%H:%M')
            finish_open_time = time.strptime(time_slot["finish_open_time"], '%H:%M')
            close_time = time.strptime(time_slot["close_time"], '%H:%M')
            start_close_time = time.strptime(time_slot["start_close_time"], '%H:%M')
            finish_close_time = time.strptime(time_slot["finish_close_time"], '%H:%M')

            if start_open_time > open_time or open_time > finish_open_time or finish_open_time > start_close_time or\
               start_close_time > close_time or close_time > finish_close_time:
                return Response(
                    {
                        'code': -1,
                        'msg': 'Time slot incorrect'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.serializer_class(
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        time_slots = request.data.pop('slots')
        context = {
            'slots': time_slots,
        }

        for time_slot in time_slots:
            open_time = time.strptime(time_slot["open_time"], '%H:%M')
            start_open_time = time.strptime(time_slot["start_open_time"], '%H:%M')
            finish_open_time = time.strptime(time_slot["finish_open_time"], '%H:%M')
            close_time = time.strptime(time_slot["close_time"], '%H:%M')
            start_close_time = time.strptime(time_slot["start_close_time"], '%H:%M')
            finish_close_time = time.strptime(time_slot["finish_close_time"], '%H:%M')

            if start_open_time > open_time or open_time > finish_open_time or finish_open_time > start_close_time or\
               start_close_time > close_time or close_time > finish_close_time:
                return Response(
                    {
                        'code': -1,
                        'msg': 'Time slot incorrect'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.serializer_class(
            instance,
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path="bulk-delete")
    def bulk_delete(slef, request):
        m.AttendanceTime.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="all")
    def get_all_times(self, request):
        return Response(
            self.serializer_class(m.AttendanceTime.objects.all(), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="all/names")
    def get_all_times_names(self, request):
        return Response(
            s.AttendanceTimeNameSerializer(m.AttendanceTime.objects.all(), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="export", renderer_classes=[XLSXRenderer])
    def export(self, request):
        queryset = self.get_queryset()
        return Response(
            s.AttendanceTimeExportSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )


class AttendanceRuleViewSet(XLSXFileMixin, viewsets.ModelViewSet):

    queryset = m.AttendanceRule.objects.all()
    serializer_class = s.AttendanceRuleSerializer
    body = EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = EXCEL_HEAD_STYLE
        ret['titles'] = [
            '部门', '考勤时间',

        ]
        return ret

    def create(self, request):
        context = {
            'attendees': request.data.pop('attendees', None),
            'nonattendees': request.data.pop('nonattendees', None),
            'events': request.data.pop('events', None),
        }
        serializer = self.serializer_class(
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        context = {
            'attendees': request.data.pop('attendees', None),
            'nonattendees': request.data.pop('nonattendees', None),
            'events': request.data.pop('events', None),
        }
        serializer = self.serializer_class(
            instance,
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(
            queryset.annotate(
                attendees_num=Count('attendancemembership', distinct=True),
                nonattendees_num=Count('unattendancemembership', distinct=True)
            )
        )
        serializer = s.AttendanceRuleListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        return Response(
            s.AttendanceRuleDetailSerializer(instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path="bulk-delete")
    def bulk_delete(slef, request):
        m.AttendanceRule.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
            status=status.HTTP_200_OK
        )


class AttendanceDailyReportViewSet(XLSXFileMixin, viewsets.ModelViewSet):

    queryset = m.AttendanceHistory.objects.all()
    serializer_class = s.AttendanceDailyReportSerializer
    body = EXCEL_BODY_STYLE

    def get_column_header(self):
        ret = EXCEL_HEAD_STYLE
        ret['titles'] = [
            '日期', '时间', '总人数', '签到', '迟到', '早退', '未签', '范围外次数'

        ]
        return ret

    def get_queryset(self):
        queryset = self.queryset
        start_date = self.request.query_params.get('startDate', None)
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(identified_on__date__gte=start_date)

        end_date = self.request.query_params.get('endDate', None)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            queryset = queryset.filter(identified_on__date__lte=end_date)

        queryset = queryset.values('id').annotate(
            attendance_date=TruncDate('identified_on'),
            attendance_rule_id=F('membership__rule'),
            attendance_time_id=F('time_slot'),
            attendance_time=Case(
                When(is_open_attend=True, then='time_slot__open_time'),
                When(is_open_attend=False, then='time_slot__close_time')
            )
        )

        queryset = queryset.values('attendance_rule_id', 'attendance_date', 'attendance_time', 'attendance_time_id',
                                   'is_open_attend').annotate(
            total_member_num=Count('membership__rule__attendees', distinct=True),
            attendees_num=Count('id', distinct=True),
            late_attendees_num=Count('id', filter=Q(is_open_attend=True, is_bad_attendance=True), distinct=True),
            early_departures_num=Count('id', filter=Q(is_open_attend=False, is_bad_attendance=False), distinct=True),
            absentees_num=F('total_member_num')-F('attendees_num'),
            outside_area_num=Count('id', filter=Q(is_right_place=False), distinct=True),
        ).order_by('-attendance_date', 'attendance_time')

        sort_str = self.request.query_params.get('sort', None)
        if sort_str:
            queryset = queryset.order_by(sort_str)

        return queryset

    @action(detail=False, methods=['post'], url_path='by-slot')
    def get_day_report(self, request):
        date = request.data.get('date')
        rule_id = request.data.get('rule')
        slot = request.data.get('slot')
        is_open_attend = request.data.get('is_open_attend')

        time_slot = get_object_or_404(m.TimeSlot, id=slot)
        rule = get_object_or_404(m.AttendanceRule, id=rule_id)

        queryset = self.queryset.filter(
            membership__rule__id=rule_id,
            identified_on__date=date,
            time_slot__id=slot,
            is_open_attend=is_open_attend
        )

        if is_open_attend:
            attendance_time = time_slot.open_time
            attendance_start_time = time_slot.start_open_time
            attendance_end_time = time_slot.finish_open_time
        else:
            attendance_time = time_slot.close_time
            attendance_start_time = time_slot.start_close_time
            attendance_end_time = time_slot.finish_close_time

        ret = queryset.aggregate(
            total_member_num=Count('membership__rule__attendees', distinct=True),
            attendees_num=Count('id', distinct=True),
            bad_attendees_num=Count('id', filter=Q(is_bad_attendance=True), distinct=True),
            outside_area_num=Count('id', filter=Q(is_right_place=False), distinct=True),
        )
        ret['attendance_dow'] = datetime.strptime(date, '%Y-%m-%d').weekday()
        ret['attendance_place'] = rule.attendance_place.name
        ret['absentees_num'] = ret['total_member_num'] - ret['attendees_num']
        ret['attendance_date'] = date
        ret['attendance_time'] = attendance_time
        ret['attendance_start_time'] = attendance_start_time
        ret['attendance_end_time'] = attendance_end_time

        return Response(
            s.AttendanceDailyReportDetailSerializer(ret).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='history-by-day')
    def get_daily_history(self, request):
        date = request.data.get('date')
        rule_id = request.data.get('rule')
        slot = request.data.get('slot')
        is_open_attend = request.data.get('is_open_attend')

        rule = get_object_or_404(m.AttendanceRule, id=rule_id)

        queryset = rule.attendees.values('id', 'user__name')

        membership = m.AttendanceMembership.objects.filter(teacher=OuterRef('pk'), rule=rule)
        queryset = queryset.annotate(membership=Subquery(membership.values('id')[:1]))

        attendance = m.AttendanceHistory.objects.filter(
            membership=OuterRef('membership'), time_slot__id=slot,
            is_open_attend=is_open_attend, identified_on__date=date
        )

        # TODO: Query optimization
        # In the time of I was developing, subquery does not support multiple columns
        queryset = queryset.annotate(
            identified_on=Subquery(attendance.values('identified_on')[:1]),
            image=Subquery(attendance.values('image')[:1]),
            is_right_place=Subquery(attendance.values('is_right_place')[:1]),
            is_bad_attendance=Subquery(attendance.values('is_bad_attendance')[:1])
        )

        page = self.paginate_queryset(queryset)
        serializer = s.AttendanceDailyHistorySerializer(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="export", renderer_classes=[XLSXRenderer])
    def export(self, request):
        queryset = self.get_queryset()
        return Response(
            s.AttendanceDailyReportExportSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )


class AttendanceStatusAPIView(views.APIView):

    def get(self, request, format=None):
        membership = m.AttendanceMembership.objects.filter(teacher=request.user.profile).order_by('-joined_on').first()
        if membership:
            today = date.today()

            # check whether today is attendance day or not
            if membership.rule.events.filter(
                is_attendance_day=False, start_date__gte=today, end_date__lte=today
            ).exists():
                return Response(
                    {
                        "code": -1,
                        "msg": "No need to attend today"
                    },
                    status=status.HTTP_200_OK
                )

            # check day attendance rule
            day_rule = get_week_day(membership.rule, today.weekday())
            if not day_rule:
                return Response(
                    {
                        "code": -1,
                        "msg": "No attendance rule today, It does not mean that you don't need to attend today"
                        "Please support administrator"
                    },
                    status=status.HTTP_200_OK
                )

            # check whether day rule has time slots
            if not day_rule.slots.exists():
                return Response(
                    {
                        "code": -1,
                        "msg": "Not time specified. It does not mean that you don't need to attend today"
                        "Please support administrator"
                    },
                    status=status.HTTP_200_OK
                )

            # following part might be a bit of complicated. But it is for convenient in app development
            current_time = datetime.now()
            ret = {
                'membership': membership.id,
                'rules': []
            }

            expand_rule_index = 0
            time_delta = timedelta(days=1)
            for slot_index, slot in enumerate(day_rule.slots.all()):
                today_checks = m.AttendanceHistory.objects.filter(
                    membership=membership, time_slot=slot, identified_on__date=today
                ).order_by('identified_on')

                open_check, close_check = None, None

                for today_check in today_checks:
                    # identified_on = today_check.identified_on.time()
                    # if identified_on >= slot.start_open_time and identified_on <= slot.finish_open_time:
                    #     open_check = today_check
                    # elif identified_on >= slot.finish_open_time and identified_on <= slot.finish_close_time:
                    #     close_check = today_check

                    if today_check.is_open_attend:
                        open_check = today_check
                    else:
                        close_check = today_check

                new_time_delta = abs(current_time - datetime.combine(today, slot.open_time))
                if time_delta > new_time_delta:
                    time_delta = new_time_delta
                    expand_rule_index = 2 * slot_index

                new_time_delta = abs(current_time - datetime.combine(today, slot.close_time))
                if time_delta > new_time_delta:
                    time_delta = new_time_delta
                    expand_rule_index = 2 * slot_index + 1

                ret['rules'].append({
                    'rule': s.TimeSlotOpenTimeSerializer(slot).data,
                    'check': s.AttendSerializer(
                        open_check,
                        context={'request': request}
                    ).data,
                    'is_expanded': False
                })
                ret['rules'].append({
                    'rule': s.TimeSlotCloseTimeSerializer(slot).data,
                    'check': s.AttendSerializer(
                        close_check,
                        context={'request': request}
                    ).data,
                    'is_expanded': False
                })

            ret['rules'][expand_rule_index]['is_expanded'] = True

            return Response(
                ret,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'msg': "You haven't any attendance membership yet"
                },
                status=status.HTTP_200_OK
            )


class AttendAPIView(views.APIView):

    def post(self, request):
        serializer = s.AttendSerializer(
            data=request.data,
            context={'user': request.user, 'imei': request.data.get('imei', None), 'request': request}
        )

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            code = 0
            data = serializer.data
        except e.FACE_RECOGNITION_NO_DATASET:
            code = -1
            data = 'No Dataset'
        except e.FACE_RECOGNITION_FAILED:
            code = -1
            data = 'Failed'
        except e.NO_ATTENDANCE_DAY:
            code = -1
            data = 'No attendance day'
        except e.OUT_OF_ATTENDANCE_TIME:
            code = -1
            data = 'Not able to attend befor or after'
        except e.TIMESLOT_MISSING:
            code = -1
            data = 'Timeslot error'
        except e.FACE_RECOGNITION_IMEI_NOT_MATCH:
            code = -1
            data = 'Imei does not match'
        except e.FACE_DETECTION_FAILED:
            code = -1
            data = 'No face detected in photo'
        except Exception:
            code = -1
            data = 'Unkonw Issue'
        finally:
            if code == 0:
                return Response(
                    {
                        'code': 0,
                        'data': data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'code': code,
                        'msg': data
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


class AttendanceCommentAPIView(views.APIView):

    def post(self, request):
        history_id = request.data.get('id')
        description = request.data.get('description', '')
        instance = get_object_or_404(m.AttendanceHistory, id=history_id)

        if description:
            instance.description = description
            instance.save()

        return Response(
            {
                'code': 0,
                'data': s.AttendSerializer(
                    instance,
                    context={'user': request.user, 'request': request}
                ).data
            },
            status=status.HTTP_200_OK
        )
