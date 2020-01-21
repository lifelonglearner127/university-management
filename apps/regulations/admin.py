from django.contrib import admin

from . import models as m


@admin.register(m.AttendancePlace)
class AttendancePlaceAdmin(admin.ModelAdmin):
    pass


@admin.register(m.TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    pass


@admin.register(m.AttendanceTime)
class AttendanceTimeAdmin(admin.ModelAdmin):
    pass


@admin.register(m.AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    pass


@admin.register(m.AttendanceEvent)
class AttendanceEventAdmin(admin.ModelAdmin):
    pass
