from datetime import timedelta, date
from django.core.management.base import BaseCommand
from apps.regulations.models import AttendanceHistory, AttendanceDatePerson, AttendanceEvent
from apps.teachers.models import TeacherProfile


class Command(BaseCommand):
    help = 'Calculate the number of attendance dates'

    def handle(self, *args, **options):
        for teacher in TeacherProfile.objects.all():
            first_membership = teacher.attendance_membership.order_by('joined_on').first()
            if first_membership is None:
                continue

            joined_date = first_membership.joined_on.date()
            period = (date.today() - joined_date).days - 1

            result = []
            membership = None
            for single_date in (joined_date + timedelta(n) for n in range(period)):
                if AttendanceDatePerson.objects.filter(teacher=teacher, date=single_date).exists():
                    continue

                try:
                    if membership is None or membership.joined_on.date() >= single_date:
                        membership = teacher.attendance_membership.filter(
                            joined_on__date__lte=single_date).order_by('-joined_on').first()

                except Exception:
                    break

                else:
                    rule = membership.rule
                    if AttendanceEvent.objects.filter(
                        rule=rule, is_attendance_day=False, start_date__gte=single_date, end_date__lte=single_date
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

                    time_rule = week_mapping[single_date.weekday()]
                    total_check = time_rule.slots.count() * 2
                    attendance_history = AttendanceHistory.objects.filter(
                        membership=membership, identified_on__date=single_date
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
                        date=single_date,
                        total_checks=total_check,
                        checks=checks,
                        late_attendances=late_attendances,
                        early_leaves=early_leaves,
                        outside_checks=outside_checks,
                        holidays=0
                    ))

            AttendanceDatePerson.objects.bulk_create(result)
