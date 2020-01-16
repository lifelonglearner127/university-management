from django.contrib import admin

from . import models as m


@admin.register(m.Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    pass


@admin.register(m.AdvertisementAudiences)
class AdvertisementAudiencesAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(m.NotificationAudiences)
class NotificationAudiencesAdmin(admin.ModelAdmin):
    pass
