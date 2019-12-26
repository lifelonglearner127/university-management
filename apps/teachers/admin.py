from django.contrib import admin

from . import models as m


@admin.register(m.Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


class TeacherImageInline(admin.TabularInline):
    model = m.TeacherImage


@admin.register(m.Teacher)
class TeacherAdmin(admin.ModelAdmin):
    inlines = [TeacherImageInline, ]
