from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s


class NewsViewSet(viewsets.ModelViewSet):

    queryset = m.News.availables.all()
    serializer_class = s.NewsAdminSerializer

    def create(self, request):
        context = {
            'author': request.data.pop('author'),
            'audiences': request.data.pop('audiences'),
        }

        serializer = self.serializer_class(
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        context = {
            'author': request.data.pop('author'),
            'audiences': request.data.pop('audiences'),
        }

        serializer = self.serializer_class(
            instance,
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

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
        instance.is_published = True
        instance.save()
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='read')
    def read(self, request, pk=None):
        instance = self.get_object()
        news_audience = instance.newsaudiences_set.filter(audience=request.user).first()
        if not news_audience:
            return Response(
                {
                    'msg': 'You are not permitted to read this news'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if not news_audience.is_published:
            return Response(
                {
                    'msg': 'This news is not published yet'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        news_audience.is_read = True
        news_audience.read_on = datetime.now()
        news_audience.save()
        return Response(
            s.NewsAudiencesAppSerializer(news_audience).data,
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
    serializer_class = s.NotificationsAdminSerializer

    def create(self, request):
        context = {
            'author': request.data.pop('author'),
            'audiences': request.data.pop('audiences'),
        }

        serializer = self.serializer_class(
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        context = {
            'author': request.data.pop('author'),
            'audiences': request.data.pop('audiences'),
        }

        serializer = self.serializer_class(
            instance,
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

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
        instance.status = m.Notifications.STATUS_SENT
        instance.save()

    @action(detail=True, url_path='read')
    def read(self, request, pk=None):
        instance = self.get_object()
        notification_audience = instance.notificationsaudiences_set.filter(
            audience=request.user
        ).first()
        if not notification_audience:
            return Response(
                {
                    'msg': 'You are not permitted to read this news'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if notification_audience.notification.status != m.Notifications.STATUS_SENT:
            return Response(
                {
                    'msg': 'This notification is not delivered yet'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        notification_audience.is_read = True
        notification_audience.read_on = datetime.now()
        notification_audience.save()
        return Response(
            s.NotificationsAudiencesAppSerializer(notification_audience).data,
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
