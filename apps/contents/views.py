from datetime import datetime, date
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from .tasks import publish_news, send_notifications


class NewsViewSet(viewsets.ModelViewSet):

    queryset = m.News.availables.all()
    serializer_class = s.NewsSerializer

    def get_queryset(self):
        queryset = self.queryset
        query_str = self.request.query_params.get('q', None)
        if query_str:
            queryset = queryset.filter(title__icontains=query_str)

        sort_str = self.request.query_params.get('sort', None)
        if sort_str:
            queryset = queryset.order_by(sort_str)

        return queryset

    def list(self, request):
        page = self.paginate_queryset(self.get_queryset())
        serializer = s.NewsListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        audiences = request.data.pop('audiences', [])
        serializer = s.NewsCreateUpdateSerializer(
            data=request.data,
            context={
                'audiences': audiences
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        audiences = request.data.pop('audiences', [])
        serializer = s.NewsCreateUpdateSerializer(
            instance,
            data=request.data,
            context={
                'audiences': audiences
            },
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None):
        instance = self.get_object()

        return Response(
            s.NewsDetailSerializer(instance).data,
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

    @action(detail=False, methods=['post'], url_path="bulk-delete")
    def bulk_delete(slef, request):
        m.News.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='audiences')
    def get_audiences_with_pagination(self, request, pk=None):
        instance = get_object_or_404(m.News, id=pk)

        audiences = instance.newsaudiences_set.all()

        query_str = request.query_params.get('q', None)
        if query_str:
            audiences = audiences.filter(audience__name__icontains=query_str)

        department_query = request.query_params.get('departments', None)
        if department_query:
            departments = department_query.split(',')
            audiences = audiences.filter(audience__profile__department__id__in=departments)

        sort_str = request.query_params.get('sort', None)
        if sort_str:
            audiences = audiences.order_by(sort_str)

        page = self.paginate_queryset(audiences)
        serializer = s.NewsAudiencesReadReportSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='publish')
    def publish(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_published:
            instance.is_published = True
            instance.published_date = date.today()
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
        if not obj.is_read:
            obj.is_read = True

        obj.recent_read_on = datetime.now()
        obj.save()
        return Response(
            s.NewsAppSerializer(
                obj.news,
                context={'audience': request.user},
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='me/all')
    def my_news(self, request):
        page = self.paginate_queryset(
            m.News.publisheds.filter(
                audiences=request.user,
            ).order_by('newsaudiences__is_read', '-updated')
        )
        serializer = s.NewsAppSerializer(
            page,
            context={'audience': request.user},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/unreads')
    def my_unread_news(self, request):
        query_filter = Q(audiences=request.user) & ~Q(newsaudiences__is_read=True)
        page = self.paginate_queryset(
            m.News.publisheds.filter(
                query_filter
            ).order_by('-updated')
        )
        serializer = s.NewsAppSerializer(
            page,
            context={'audience': request.user},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/reads')
    def my_read_news(self, request):
        query_filter = Q(audiences=request.user) & Q(newsaudiences__is_read=True)
        page = self.paginate_queryset(
            m.News.publisheds.filter(
                query_filter
            ).order_by('-newsaudiences__recent_read_on')
        )
        serializer = s.NewsAppSerializer(
            page,
            context={'audience': request.user},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="me/unread-count")
    def my_unread_news_count(self, request):
        query_filter = Q(audiences=request.user) & ~Q(newsaudiences__is_read=True)
        my_unread_count = m.News.publisheds.filter(query_filter).count()
        return Response(
            {
                'count': my_unread_count
            },
            status=status.HTTP_200_OK
        )


class NotificationViewSet(viewsets.ModelViewSet):

    queryset = m.Notification.availables.all()
    serializer_class = s.NotificationSerializer

    def create(self, request):
        audiences = request.data.pop('audiences', [])
        serializer = s.NotificationCreateUpdateSerializer(
            data=request.data,
            context={
                'audiences': audiences
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        audiences = request.data.pop('audiences', [])
        serializer = s.NotificationCreateUpdateSerializer(
            instance,
            data=request.data,
            context={
                'audiences': audiences
            },
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = s.NotificationDetailSerializer(instance)
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

    @action(detail=True, url_path='audiences')
    def get_audiences_with_pagination(self, request, pk=None):
        instance = get_object_or_404(m.Notification, id=pk)

        audiences = instance.notificationaudiences_set.all()

        query_str = request.query_params.get('q', None)
        if query_str:
            audiences = audiences.filter(audience__name__icontains=query_str)

        department_query = request.query_params.get('departments', None)
        if department_query:
            departments = department_query.split(',')
            audiences = audiences.filter(audience__profile__department__id__in=departments)

        sort_str = request.query_params.get('sort', None)
        if sort_str:
            audiences = audiences.order_by(sort_str)

        page = self.paginate_queryset(audiences)
        serializer = s.NotificationAudiencesReadReportSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path="send")
    def send(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_sent:
            instance.is_sent = True
            instance.sent_on = datetime.now()
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
        if not instance.is_sent:
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

        obj, created = m.NotificationAudiences.objects.get_or_create(
            notification=instance, audience=request.user
        )
        obj.is_read = True
        obj.recent_read_on = datetime.now()
        obj.save()
        return Response(
            s.NotificationAppSerializer(
                obj.notification,
                context={'audience': request.user},
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='me/all')
    def my_notifications(self, request):
        page = self.paginate_queryset(
            m.Notification.sents.filter(
                audiences=request.user,
            ).order_by('notificationsaudiences__is_read', '-updated')
        )
        serializer = s.NotificationAppSerializer(
            page,
            context={'audience': request.user},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/unreads')
    def my_unread_notifications(self, request):
        query_filter = Q(audiences=request.user) & ~Q(notificationsaudiences__is_read=True)
        page = self.paginate_queryset(
            m.Notification.sents.filter(
                query_filter
            ).order_by('-updated')
        )
        serializer = s.NotificationAppSerializer(
            page,
            context={'audience': request.user},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/reads')
    def my_read_notifications(self, request):
        query_filter = Q(audiences=request.user) & Q(notificationsaudiences__is_read=True)
        page = self.paginate_queryset(
            m.Notification.sents.filter(
                query_filter
            ).order_by('-updated')
        )
        serializer = s.NotificationAppSerializer(
            page,
            context={'audience': request.user},
            many=True
        )
        return self.get_paginated_response(serializer.data)
