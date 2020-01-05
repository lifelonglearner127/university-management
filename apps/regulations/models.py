from django.db import models
from ..teachers.models import TeacherProfile


class AttendancePlace(models.Model):

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


class AttendanceTime(models.Model):

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    slots = models.ManyToManyField(TimeSlot)


class AttendanceManagement(models.Model):
    pass
