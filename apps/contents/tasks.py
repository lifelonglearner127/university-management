import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from config.celery import app
from django.shortcuts import get_object_or_404

from . import models as m


channel_layer = get_channel_layer()


@app.task
def publish_news(context):
    news = get_object_or_404(m.News, id=context['news'])
    for audience in news.audiences.all():
        if not audience.channel_name:
            continue

        query_filter = m.Q(audiences=audience) & ~m.Q(newsaudiences__is_read=True)
        my_unread_count = m.News.publisheds.filter(query_filter).count()

        async_to_sync(channel_layer.send)(
            audience.channel_name,
            {
                'type': 'notify',
                'data': json.dumps({
                    'code': 0,
                    'type': 'news',
                    'unreadCount': my_unread_count
                })
            }
        )


@app.task
def send_notifications(context):
    notification = get_object_or_404(m.Notifications, id=context['notification'])

    for audience in notification.audiences.all():
        if not audience.channel_name:
            continue

        query_filter = m.Q(audiences=audience) & ~m.Q(notificationsaudiences__is_read=True)
        my_unread_count = m.Notifications.sents.filter(query_filter).count()

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
