from datetime import timedelta, date
from config.celery import app
from apps.teachers.models import TeacherProfile
from apps.regulations.models import AttendanceHistory, AttendanceDatePerson, AttendanceEvent


@app.task
def update_attendance_report():
    today = date.today()
    yesterday = today - timedelta(days=1)
    result = []

    for teacher in TeacherProfile.objects.all():
        if AttendanceDatePerson.objects.filter(teacher=teacher, date=yesterday).exists():
            continue

        membership = teacher.attendance_membership.filter(
            joined_on__date__lte=yesterday).order_by('-joined_on').first()
        if membership is None:
            continue

        rule = membership.rule
        if AttendanceEvent.objects.filter(
            rule=rule, is_attendance_day=False, start_date__gte=yesterday, end_date__lte=yesterday
        ).exists():
            pass

        week_mapping = {
            0: rule.mon,
            1: rule.tue,
            2: rule.wed,
            3: rule.thr,
            4: rule.fri,
            5: rule.sat,
            6: rule.sun
        }
        time_rule = week_mapping[yesterday.weekday()]
        total_check = time_rule.slots.count() * 2
        attendance_history = AttendanceHistory.objects.filter(
            membership=membership, identified_on__date=yesterday
        )
        checks = attendance_history.count()
        late_attendances = 0
        early_leaves = 0
        outside_checks = 0
        for item in attendance_history:
            if item.is_open_attend and item.is_bad_attendance:
                late_attendances += 1

            if not item.is_open_attend and item.is_bad_attendance:
                early_leaves += 1

            if not item.is_right_place:
                outside_checks += 1

        result.append(AttendanceDatePerson(
            teacher=teacher,
            date=yesterday,
            total_checks=total_check,
            checks=checks,
            late_attendances=late_attendances,
            early_leaves=early_leaves,
            outside_checks=outside_checks,
            holidays=0
        ))

    AttendanceDatePerson.objects.bulk_create(result)
