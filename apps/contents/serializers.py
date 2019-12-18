from rest_framework import serializers

from . import models as m
from ..accounts.serializers import UserNameSerializer
from ..core.serializers import TMSChoiceField


class NewsAudiencesAdminSerializer(serializers.ModelSerializer):
    """NewsAudience Serializer for web manager
    """
    recent_read_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    audience = UserNameSerializer(read_only=True)

    class Meta:
        model = m.NewsAudiences
        exclude = (
            'id', 'news',
        )


class NewsBodylessSerializer(serializers.ModelSerializer):
    """News Serializer without news body

    This serializer is used for listing news in apps
    """
    author = UserNameSerializer(read_only=True)

    class Meta:
        model = m.News
        fields = (
            'id', 'title', 'author', 'is_published',
        )


class NewsSerializer(serializers.ModelSerializer):
    """News Serializer

    This serializer is used for creating & updating news instance
    """
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.News
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['author'] = UserNameSerializer(instance.author).data
        ret['audiences'] = UserNameSerializer(
            instance.audiences, many=True
        ).data

        return ret


class NewsAdminSerializer(serializers.ModelSerializer):
    """News Serializer for web manager

    This serializer is used for displaying the read status of the audiences
    """
    author = UserNameSerializer(read_only=True)
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    audiences = NewsAudiencesAdminSerializer(
        source='newsaudiences_set', many=True, read_only=True
    )

    class Meta:
        model = m.News
        fields = '__all__'


class NewsAppSerializer(serializers.ModelSerializer):
    """News serializer for teacher app
    """
    author = UserNameSerializer()
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    meta = serializers.SerializerMethodField()

    class Meta:
        model = m.News
        fields = (
            'id', 'title', 'author', 'is_published', 'is_deleted', 'meta',
            'created', 'updated'
        )

    def get_meta(self, instance):
        news_audience = m.NewsAudiences.objects.filter(
            news=instance,
            audience=self.context.get('audience', None)
        ).first()
        if news_audience:
            return {
                'recent_read_on':
                news_audience.recent_read_on.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': news_audience.is_read
            }
        else:
            return {
                'recent_read_on': None,
                'is_read': False
            }


class NotificationsAudiencesAdminSerializer(serializers.ModelSerializer):
    """NotificationsAudience Serializer for web manager
    """
    recent_read_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    audience = UserNameSerializer(read_only=True)

    class Meta:
        model = m.NotificationsAudiences
        exclude = (
            'id', 'notification',
        )


class NotificationSerializer(serializers.ModelSerializer):
    """News Serializer

    This serializer is used for creating & updating notification instance
    """
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.Notifications
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['author'] = UserNameSerializer(instance.author).data
        ret['audiences'] = UserNameSerializer(
            instance.audiences, many=True
        ).data

        return ret


class NotificationsAdminSerializer(serializers.ModelSerializer):
    """Notification Serializer for web manager

    This serializer is used for displaying the read status of the audiences
    """
    author = UserNameSerializer(read_only=True)
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    audiences = NotificationsAudiencesAdminSerializer(
        source='notificationsaudiences_set', many=True, read_only=True
    )
    status = TMSChoiceField(m.Notifications.STATUS)

    class Meta:
        model = m.Notifications
        fields = '__all__'


class NotificationsAppSerializer(serializers.ModelSerializer):
    """Notifications Serializer for teacher app
    """
    status = TMSChoiceField(m.Notifications.STATUS)
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    meta = serializers.SerializerMethodField()

    class Meta:
        model = m.Notifications
        fields = (
            'id', 'title', 'body', 'author', 'status', 'meta',
            'created', 'updated',
        )

    def get_meta(self, instance):
        notification_audience = m.NotificationsAudiences.objects.filter(
            notification=instance,
            audience=self.context.get('audience', None)
        ).first()
        if notification_audience:
            return {
                'recent_read_on':
                notification_audience.recent_read_on.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': notification_audience.is_read
            }
        else:
            return {
                'recent_read_on': None,
                'is_read': False
            }
