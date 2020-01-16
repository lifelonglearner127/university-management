import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from config.celery import app
from django.shortcuts import get_object_or_404

from . import models as m


channel_layer = get_channel_layer()


@app.task
def publish_advertisement(context):
    advertisement = get_object_or_404(m.Advertisement, id=context['advertisement'])
    for audience in advertisement.audiences.all():
        if not audience.channel_name:
            continue

        query_filter = m.Q(audiences=audience) & ~m.Q(advertisementaudiences__is_read=True)
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

    for audience in notification.audiences.all():
        if not audience.channel_name:
            continue

        query_filter = m.Q(audiences=audience) & ~m.Q(notificationsaudiences__is_read=True)
        my_unread_count = m.Notification.sents.filter(query_filter).count()

        async_to_sync(channel_layer.send)(
            audience.channel_name,
            {
                'type': 'notify',
                'data': json.dumps({
                    'code': 0,
                    'type': 'notification',
                    'unreadCount': my_unread_count
                })
            }
        )
