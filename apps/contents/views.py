from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from .tasks import publish_news, send_notifications


class NewsViewSet(viewsets.ModelViewSet):

    queryset = m.News.availables.all()
    serializer_class = s.NewsSerializer

    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, url_path='publish')
    def publish(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_published:
            instance.is_published = True
            instance.save()
            publish_news.apply_async(
                args=[{
                    'news': instance.id
                }]
            )
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='read')
    def read(self, request, pk=None):
        instance = self.get_object()

        if not instance.is_published:
            return Response(
                {
                    'msg': 'This news is not published yet'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if request.user not in instance.audiences.all():
            return Response(
                {
                    'msg': 'You are not permitted to read this news'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        obj, created = m.NewsAudiences.objects.get_or_create(
            news=instance, audience=request.user
        )
        obj.is_read = True
        obj.read_on = datetime.now()
        obj.save()
        return Response(
            s.NewsAudiencesAppSerializer(obj).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='me/all')
    def my_news(self, request):
        page = self.paginate_queryset(
            m.NewsAudiences.objects.filter(
                audience=request.user,
                news__is_published=True,
                news__is_deleted=False
            ).order_by('-news__updated')
        )
        serializer = s.NewsAudiencesAppSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/unreads')
    def my_unread_news(self, request):
        page = self.paginate_queryset(
            m.NewsAudiences.objects.filter(
                audience=request.user,
                is_read=False,
                news__is_published=True,
                news__is_deleted=False
            ).order_by('-news__updated')
        )
        serializer = s.NewsAudiencesAppSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/reads')
    def my_read_news(self, request):
        page = self.paginate_queryset(
            m.NewsAudiences.objects.filter(
                audience=request.user,
                is_read=True,
                news__is_published=True,
                news__is_deleted=False
            ).order_by('-news__updated')
        )
        serializer = s.NewsAudiencesAppSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class NotificationsViewSet(viewsets.ModelViewSet):

    queryset = m.Notifications.availables.all()
    serializer_class = s.NotificationSerializer

    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, url_path="send")
    def send(self, request, pk=None):
        instance = self.get_object()
        if instance.status != m.Notifications.STATUS_SENT:
            instance.status = m.Notifications.STATUS_SENT
            instance.save()
            send_notifications.apply_async(
                args=[{
                    'notification': instance.id
                }]
            )
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='read')
    def read(self, request, pk=None):
        instance = self.get_object()
        if instance.status != m.Notifications.STATUS_SENT:
            return Response(
                {
                    'msg': 'This notification is not delivered yet'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if request.user not in instance.audiences.all():
            return Response(
                {
                    'msg': 'You are not permitted to read this news'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        obj, created = m.NotificationsAudiences.objects.get_or_create(
            notification=instance, audience=request.user
        )
        obj.is_read = True
        obj.read_on = datetime.now()
        obj.save()
        return Response(
            s.NotificationsAudiencesAppSerializer(obj).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='me/all')
    def my_notifications(self, request):
        page = self.paginate_queryset(
            m.NotificationsAudiences.objects.filter(
                audience=request.user,
                notification__status=m.Notifications.STATUS_SENT,
                notification__is_deleted=False,
            ).order_by('-notification__updated')
        )
        serializer = s.NotificationsAudiencesAppSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/unreads')
    def my_unread_notifications(self, request):
        page = self.paginate_queryset(
            m.NotificationsAudiences.objects.filter(
                audience=request.user,
                is_read=False,
                notification__status=m.Notifications.STATUS_SENT,
                notification__is_deleted=False
            ).order_by('-notification__updated')
        )
        serializer = s.NotificationsAudiencesAppSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/reads')
    def my_read_notifications(self, request):
        page = self.paginate_queryset(
            m.NotificationsAudiences.objects.filter(
                audience=request.user,
                is_read=True,
                notification__status=m.Notifications.STATUS_SENT,
                notification__is_deleted=False,
            ).order_by('-notification__updated')
        )
        serializer = s.NotificationsAudiencesAppSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
