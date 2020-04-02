from itertools import islice
from rest_framework import serializers

from . import models as m
from ..accounts.serializers import UserNameSerializer
from ..teachers.serializers import DepartmentSerializer


batch_size = 100


class AdvertisementAudienceSerializer(serializers.ModelSerializer):

    recent_read_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = m.AdvertisementAudiences
        exclude = (
            'advertisement',
        )


class AdvertisementAudiencesReadReportSerializer(serializers.ModelSerializer):

    audience = UserNameSerializer()
    department = DepartmentSerializer(source='audience.profile.department')

    class Meta:
        model = m.AdvertisementAudiences
        fields = (
            'id', 'audience', 'department', 'recent_read_on', 'is_read'
        )


class AdvertisementSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Advertisement
        fields = '__all__'


class AdvertisementCreateUpdateSerializer(serializers.ModelSerializer):
    """Advertisement Serializer

    This serializer is used for creating & updating advertisement instance
    """
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.Advertisement
        fields = '__all__'

    def create(self, validated_data):
        advertisement = m.Advertisement.objects.create(**validated_data)
        audience_ids = self.context.pop('audiences', [])
        audiences = m.User.objects.filter(id__in=audience_ids)
        objs = (m.AdvertisementAudiences(advertisement=advertisement, audience=audience) for audience in audiences)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.AdvertisementAudiences.objects.bulk_create(batch, batch_size)

        return advertisement

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        old_audience_ids = set(instance.audiences.values_list('id', flat=True))
        new_audience_ids = set(self.context.pop('audiences', []))
        m.AdvertisementAudiences.objects.filter(
            advertisement=instance, audience__id__in=old_audience_ids.difference(new_audience_ids)
        ).delete()

        new_audiences = m.User.objects.filter(id__in=new_audience_ids.difference(old_audience_ids))
        objs = (m.AdvertisementAudiences(advertisement=instance, audience=audience) for audience in new_audiences)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.AdvertisementAudiences.objects.bulk_create(batch, batch_size)

        instance.save()
        return instance


class AdvertisementListSerializer(serializers.ModelSerializer):
    """Advertisement List Serializer without advertisement body

    This serializer is used for listing advertisement in web table
    """
    author = UserNameSerializer(read_only=True)

    class Meta:
        model = m.Advertisement
        fields = (
            'id', 'title', 'author', 'is_published', 'published_date',
        )


class AdvertisementDetailSerializer(serializers.ModelSerializer):

    author = UserNameSerializer(read_only=True)
    read_report = serializers.SerializerMethodField()

    class Meta:
        model = m.Advertisement
        fields = (
            'id', 'title', 'body', 'author', 'is_published', 'published_date', 'audiences',
            'read_report',
        )

    def get_read_report(self, instance):
        total_count = instance.audiences.count()
        read_count = m.AdvertisementAudiences.objects.filter(advertisement=instance, is_read=True).count()
        return {
            'total_count': total_count,
            'read_count': read_count,
            'unread_count': total_count - read_count
        }


class AdvertisementAppSerializer(serializers.ModelSerializer):
    """Advertisement serializer for teacher app
    """
    advertisement = AdvertisementListSerializer()

    class Meta:
        model = m.AdvertisementAudiences
        fields = (
            'id', 'advertisement', 'is_read', 'recent_read_on',
        )


class NotificationAudiencesAdminSerializer(serializers.ModelSerializer):
    """NotificationsAudience Serializer for web manager
    """
    recent_read_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    audience = UserNameSerializer(read_only=True)

    class Meta:
        model = m.NotificationAudiences
        exclude = (
            'id', 'notification',
        )


class NotificationAudiencesSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.NotificationAudiences
        exclude = (
            'notification',
        )


class NotificationSerializer(serializers.ModelSerializer):

    author = UserNameSerializer()

    class Meta:
        model = m.Notification
        fields = '__all__'


class NotificationCreateUpdateSerializer(serializers.ModelSerializer):
    """Notification Create or Update Serializer

    This serializer is used for creating & updating notification instance
    """
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.Notification
        fields = '__all__'

    def create(self, validated_data):
        notification = m.Notification.objects.create(**validated_data)
        audience_ids = self.context.pop('audiences', [])
        audiences = m.User.objects.filter(id__in=audience_ids)
        objs = (m.NotificationAudiences(notification=notification, audience=audience) for audience in audiences)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.NotificationAudiences.objects.bulk_create(batch, batch_size)

        return notification

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        old_audience_ids = set(instance.audiences.values_list('id', flat=True))
        new_audience_ids = set(self.context.pop('audiences', []))
        m.NotificationAudiences.objects.filter(
            notification=instance, audience__id__in=old_audience_ids.difference(new_audience_ids)
        ).delete()

        new_audiences = m.User.objects.filter(id__in=new_audience_ids.difference(old_audience_ids))
        objs = (m.NotificationAudiences(notification=instance, audience=audience) for audience in new_audiences)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.NotificationAudiences.objects.bulk_create(batch, batch_size)

        instance.save()
        return instance


class NotificationListSerializer(serializers.ModelSerializer):

    author = UserNameSerializer(read_only=True)
    sent_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = m.Notification
        fields = (
            'id', 'title', 'author', 'is_sent', 'sent_on',
        )


class NotificationListAppSerializer(serializers.ModelSerializer):

    sent_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = m.Notification
        fields = (
            'id', 'title', 'body', 'is_sent', 'sent_on',
        )


class NotificationDetailSerializer(serializers.ModelSerializer):

    author = UserNameSerializer(read_only=True)
    read_report = serializers.SerializerMethodField()
    sent_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = m.Notification
        fields = (
            'id', 'title', 'body', 'author', 'is_sent', 'sent_on', 'audiences',
            'read_report',
        )

    def get_read_report(self, instance):
        total_count = instance.audiences.count()
        read_count = m.NotificationAudiences.objects.filter(notification=instance, is_read=True).count()
        return {
            'total_count': total_count,
            'read_count': read_count,
            'unread_count': total_count - read_count
        }


class NotificationAudiencesReadReportSerializer(serializers.ModelSerializer):

    audience = UserNameSerializer()
    department = DepartmentSerializer(source='audience.profile.department')

    class Meta:
        model = m.NotificationAudiences
        fields = (
            'id', 'audience', 'department', 'recent_read_on', 'is_read'
        )


class NotificationAppSerializer(serializers.ModelSerializer):
    """Notifications Serializer for teacher app
    """
    notification = NotificationListAppSerializer()
    recent_read_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = m.NotificationAudiences
        fields = (
            'id', 'notification', 'is_read', 'recent_read_on',
        )


class NotificationAppWithUnReadCountSerializer(serializers.ModelSerializer):
    """Notifications Serializer for teacher app
    """
    notification = NotificationListAppSerializer()
    unread_count = serializers.SerializerMethodField()
    recent_read_on = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = m.NotificationAudiences
        fields = (
            'id', 'notification', 'is_read', 'recent_read_on', 'unread_count'
        )

    def get_unread_count(self, instance):
        return m.NotificationAudiences.objects.filter(
            notification__is_sent=True, notification__is_deleted=False,
            audience=self.context.get('user'), is_read=False,  is_deleted=False
        ).count()
