from itertools import islice
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from config.celery import app
from django.shortcuts import get_object_or_404

from . import models as m


channel_layer = get_channel_layer()


@app.task
def publish_news(context):
    news = get_object_or_404(m.News, id=context['news'])

    batch_size = 100
    objs = (
        m.NewsAudiences(
            news=news, audience=audience
        ) for audience in news.audiences.all()
    )
    while True:
        batch = list(islice(objs, batch_size))
        if not batch:
            break
        m.NewsAudiences.objects.bulk_create(batch, batch_size)

    channel_names = news.audiences.values_list('channel_name', flat=True)
    for channel_name in channel_names:
        if not channel_name:
            continue

        async_to_sync(channel_layer.send)(
            channel_name,
            {
                'type': 'notify',
                'data': json.dumps({
                    'code': 0,
                    'type': 'news'
                })
            }
        )


@app.task
def send_notifications(context):
    notification = get_object_or_404(m.Notifications, id=context['notification'])

    batch_size = 100
    objs = (
        m.NotificationsAudiences(
            notification=notification, audience=audience
        ) for audience in notification.audiences.all()
    )
    while True:
        batch = list(islice(objs, batch_size))
        if not batch:
            break
        m.NotificationsAudiences.objects.bulk_create(batch, batch_size)

    channel_names = notification.audiences.values_list('channel_name', flat=True)
    for channel_name in channel_names:
        if not channel_name:
            continue

        async_to_sync(channel_layer.send)(
            channel_name,
            {
                'type': 'notify',
                'data': json.dumps({
                    'code': 0,
                    'type': 'notification'
                })
            }
        )
