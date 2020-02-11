import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from config.celery import app
from django.shortcuts import get_object_or_404
from django.db.models import Q
from . import models as m
from .serializers import NotificationAppSerializer


channel_layer = get_channel_layer()


@app.task
def publish_advertisement(context):
    advertisement = get_object_or_404(m.Advertisement, id=context['advertisement'])
    for audience in advertisement.audiences.all():
        if not audience.channel_name:
            continue

        query_filter = Q(audiences=audience) & ~Q(advertisementaudiences__is_read=True)
        my_unread_count = m.Advertisement.publisheds.filter(query_filter).count()

        async_to_sync(channel_layer.send)(
            audience.channel_name,
            {
                'type': 'notify',
                'data': json.dumps({
                    'code': 0,
                    'type': 'advertisement',
                    'unreadCount': my_unread_count
                })
            }
        )


@app.task
def send_notifications(context):
    notification = get_object_or_404(m.Notification, id=context['notification'])

    for notification_audience in notification.notificationaudiences_set.all():
        if not notification_audience.audience.channel_name:
            continue

        my_unread_count = m.NotificationAudiences.objects.filter(
            notification__is_sent=True, notification__is_deleted=False,
            audience=notification_audience.audience, is_read=False,  is_deleted=False
        ).count()

        async_to_sync(channel_layer.send)(
            notification_audience.audience.channel_name,
            {
                'type': 'notify',
                'data': {
                    'code': 0,
                    'type': 'notification',
                    'data': NotificationAppSerializer(notification_audience).data,
                    'unreadCount': my_unread_count
                }
            }
        )
