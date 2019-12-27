from django.contrib import admin

from . import models as m


@admin.register(m.Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.TeacherImage)
class TeacherImageInline(admin.ModelAdmin):
    pass


@admin.register(m.Teacher)
class TeacherAdmin(admin.ModelAdmin):
    pass
