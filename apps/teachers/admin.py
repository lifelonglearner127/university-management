from django.contrib import admin

from . import models as m


@admin.register(m.Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Position)
class PositionAdmin(admin.ModelAdmin):
    pass


@admin.register(m.TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(m.TeacherImage)
class TeacherImageAdmin(admin.ModelAdmin):
    pass
