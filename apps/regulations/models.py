from django.db import models
from ..teachers.models import TeacherProfile
from ..core.models import TimeStampedModel


class AttendancePlace(TimeStampedModel):

    name = models.CharField(
        max_length=100
    )

    address = models.CharField(
        max_length=500,
    )

    longitude = models.DecimalField(
        max_digits=20,
        decimal_places=10
    )

    latitude = models.DecimalField(
        max_digits=20,
        decimal_places=10
    )

    radius = models.PositiveIntegerField(
        default=100
    )


class TimeSlot(models.Model):

    open_time = models.TimeField()

    start_open_time = models.TimeField()

    finish_open_time = models.TimeField()

    close_time = models.TimeField()

    start_close_time = models.TimeField()

    finish_close_time = models.TimeField()


class AttendanceTime(TimeStampedModel):

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    slots = models.ManyToManyField(TimeSlot)


class AttendanceRule(TimeStampedModel):

    name = models.CharField(
        max_length=100
    )

    # TODO: merge attendees & nonattendees in the next phase
    attendees = models.ManyToManyField(
        TeacherProfile,
        through="AttendanceMembership",
        related_name="attendee_rules"
    )

    nonattendees = models.ManyToManyField(
        TeacherProfile,
        through="UnAttendanceMembership",
        related_name="nonattendee_rules"
    )

    attendance_place = models.ForeignKey(
        AttendancePlace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    mon = models.ForeignKey(
        AttendanceTime,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mons",
    )

    tue = models.ForeignKey(
        AttendanceTime,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tues",
    )

    wed = models.ForeignKey(
        AttendanceTime,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="weds",
    )

    thr = models.ForeignKey(
        AttendanceTime,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="thrs",
    )

    fri = models.ForeignKey(
        AttendanceTime,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fris",
    )

    sat = models.ForeignKey(
        AttendanceTime,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sats",
    )

    sun = models.ForeignKey(
        AttendanceTime,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suns",
    )


class AttendanceMembership(models.Model):

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='attendance_membership'
    )

    rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.CASCADE
    )

    joined_on = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.teacher.user.name}'s' - {self.rule.name}"


class UnAttendanceMembership(models.Model):

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE
    )

    rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.CASCADE
    )

    joined_on = models.DateTimeField(
        auto_now_add=True
    )


class AttendanceEvent(models.Model):

    rule = models.ForeignKey(
        AttendanceRule,
        on_delete=models.CASCADE,
        related_name='events'
    )

    is_attendance_day = models.BooleanField(
        default=True
    )

    start_date = models.DateField()

    end_date = models.DateField()

    description = models.TextField()


def attendance_image_path(instance, filename):
    year = instance.identified_on.year
    month = instance.identified_on.month
    day = instance.identified_on.month
    return f"{year}/{month}/{day}/{filename}"


class AttendanceHistory(models.Model):

    membership = models.ForeignKey(
        AttendanceMembership,
        on_delete=models.CASCADE,
        related_name='history'
    )

    # You might think why below 3 fields are necessary in this history model. I thought so.
    # I added these fields for better sql performance
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_open_attend = models.BooleanField(
        default=True
    )

    is_bad_attendance = models.BooleanField(
        default=False
    )

    identified_on = models.DateTimeField(
        auto_now_add=True
    )

    image = models.ImageField(upload_to=attendance_image_path)

    longitude = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        null=True,
        blank=True
    )

    latitude = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        null=True,
        blank=True
    )

    is_right_place = models.BooleanField(
        default=True
    )
