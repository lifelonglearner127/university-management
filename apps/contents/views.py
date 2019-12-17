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
                audience=request.user, news__is_deleted=False
            ).order_by('-news__updated')
        )
        serializer = s.NewsAudiencesAppSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/unreads')
    def my_unread_news(self, request):
        page = self.paginate_queryset(
            m.NewsAudiences.objects.filter(
                audience=request.user, is_read=False, news__is_deleted=False
            ).order_by('-news__updated')
        )
        serializer = s.NewsAudiencesAppSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/reads')
    def my_read_news(self, request):
        page = self.paginate_queryset(
            m.NewsAudiences.objects.filter(
                audience=request.user, is_read=True, news__is_deleted=False
            ).order_by('-news__updated')
        )
        serializer = s.NewsAudiencesAppSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class NotificationsViewSet(viewsets.ModelViewSet):

    queryset = m.Notifications.objects.all()
    serializer_class = s.NotificationsSerializer

    def create(self, request):
        context = {
            'author': request.data.pop('author')
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
            'author': request.data.pop('author')
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

    @action(detail=True, url_path='read')
    def read(self, request, pk=None):
        pass
