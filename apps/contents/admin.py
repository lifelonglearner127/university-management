from django.contrib import admin

from . import models as m


@admin.register(m.News)
class NewsAdmin(admin.ModelAdmin):
    pass


@admin.register(m.NewsAudiences)
class NewsAudiencesAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(m.NotificationAudiences)
class NotificationAudiencesAdmin(admin.ModelAdmin):
    pass
