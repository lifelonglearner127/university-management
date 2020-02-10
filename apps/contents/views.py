from datetime import datetime, date
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s
from .tasks import publish_advertisement, send_notifications


class AdvertisementViewSet(viewsets.ModelViewSet):

    queryset = m.Advertisement.availables.all()
    serializer_class = s.AdvertisementSerializer

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
        serializer = s.AdvertisementListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        audiences = request.data.pop('audiences', [])
        serializer = s.AdvertisementCreateUpdateSerializer(
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
        serializer = s.AdvertisementCreateUpdateSerializer(
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
            s.AdvertisementDetailSerializer(instance).data,
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
        m.Advertisement.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response(
            {
                'msg': 'Delete successfully'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='audiences')
    def get_audiences_with_pagination(self, request, pk=None):
        instance = get_object_or_404(m.Advertisement, id=pk)

        audiences = instance.advertisementaudiences_set.all()

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
        serializer = s.AdvertisementAudiencesReadReportSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, url_path='publish')
    def publish(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_published:
            instance.is_published = True
            instance.published_date = date.today()
            instance.save()
            # publish_advertisement.apply_async(
            #     args=[{
            #         'advertisement': instance.id
            #     }]
            # )
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
                    'msg': 'This advertisement is not published yet'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if request.user not in instance.audiences.all():
            return Response(
                {
                    'msg': 'You are not permitted to read this advertisement'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        obj, created = m.AdvertisementAudiences.objects.get_or_create(
            advertisement=instance, audience=request.user
        )
        if not obj.is_read:
            obj.is_read = True

        obj.recent_read_on = datetime.now()
        obj.save()
        return Response(
            s.AdvertisementAppSerializer(obj).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='me/all')
    def my_advertisement(self, request):
        page = self.paginate_queryset(
            m.AdvertisementAudiences.objects.filter(
                advertisement__is_published=True, advertisement__is_deleted=False, audience=request.user
            ).order_by('is_read', '-recent_read_on')
        )
        serializer = s.AdvertisementAppSerializer(
            page,
            context={'audience': request.user},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/unreads')
    def my_unread_advertisement(self, request):
        page = self.paginate_queryset(
            m.AdvertisementAudiences.objects.filter(
                advertisement__is_published=True, advertisement__is_deleted=False, audience=request.user, is_read=False
            ).order_by('-advertisement__updated')
        )
        serializer = s.AdvertisementAppSerializer(
            page,
            context={'audience': request.user},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/reads')
    def my_read_advertisement(self, request):
        page = self.paginate_queryset(
            m.AdvertisementAudiences.objects.filter(
                advertisement__is_published=True, advertisement__is_deleted=False, audience=request.user, is_read=True
            ).order_by('-recent_read_on')
        )
        serializer = s.AdvertisementAppSerializer(
            page,
            context={'audience': request.user},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="me/unread-count")
    def my_unread_advertisement_count(self, request):
        my_unread_count = m.AdvertisementAudiences.objects.filter(
            advertisement__is_published=True, advertisement__is_deleted=False, audience=request.user, is_read=False
        ).count()
        return Response(
            {
                'count': my_unread_count
            },
            status=status.HTTP_200_OK
        )


class NotificationViewSet(viewsets.ModelViewSet):

    queryset = m.Notification.availables.all()
    serializer_class = s.NotificationSerializer

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
        serializer = s.NotificationListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

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
                    'msg': 'You are not permitted to read this advertisement'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        obj, created = m.NotificationAudiences.objects.get_or_create(
            notification=instance, audience=request.user
        )
        if not obj.is_read:
            obj.is_read = True

        obj.recent_read_on = datetime.now()
        obj.save()
        return Response(
            s.NotificationAppSerializer(obj).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='me/all')
    def my_notifications(self, request):
        page = self.paginate_queryset(
            m.NotificationAudiences.objects.filter(
                notification__is_sent=True, notification__is_deleted=False, audience=request.user
            ).order_by('is_read', '-recent_read_on')
        )

        serializer = s.NotificationAppSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/unreads')
    def my_unread_notifications(self, request):
        page = self.paginate_queryset(
            m.NotificationAudiences.objects.filter(
                notification__is_sent=True, notification__is_deleted=False, audience=request.user, is_read=False
            ).order_by('is_read', '-recent_read_on')
        )

        serializer = s.NotificationAppSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me/reads')
    def my_read_notifications(self, request):
        page = self.paginate_queryset(
            m.NotificationAudiences.objects.filter(
                notification__is_sent=True, notification__is_deleted=False, audience=request.user, is_read=True
            ).order_by('is_read', '-recent_read_on')
        )

        serializer = s.NotificationAppSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="me/unread-count")
    def my_unread_notifications_count(self, request):
        my_unread_count = m.NotificationAudiences.objects.filter(
            notification__is_sent=True, notification__is_deleted=False, audience=request.user, is_read=False
        ).count()
        return Response(
            {
                'count': my_unread_count
            },
            status=status.HTTP_200_OK
        )


class AdvertisementAppDetailView(DetailView):

    template_name = "contents/advertisements.html"
    queryset = m.Advertisement.objects.all()

    def get(self, request, *args, **kwargs):
        instance = super().get_object()
        return render(request, self.template_name, {
            'title': instance.title,
            'published_date': instance.published_date,
            'author': instance.author,
            'body': instance.body,
        })
