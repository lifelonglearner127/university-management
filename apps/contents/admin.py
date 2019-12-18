from django.contrib import admin

from . import models as m

@admin.register(m.News)
class NewsAdmin(admin.ModelAdmin):
    pass


@admin.register(m.NewsAudiences)
class NewsAudiencesAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    pass


@admin.register(m.NotificationsAudiences)
class NotificationsAudiencesAdmin(admin.ModelAdmin):
    pass
