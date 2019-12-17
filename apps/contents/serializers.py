from itertools import islice
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from . import models as m
from ..accounts.serializers import UserNameSerializer


class NewsAudiencesAdminSerializer(serializers.ModelSerializer):
    """NewsAudience Serializer for web manager
    """
    read_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    audience = UserNameSerializer(read_only=True)

    class Meta:
        model = m.NewsAudiences
        exclude = (
            'id', 'news',
        )


class NewsBodylessSerializer(serializers.ModelSerializer):

    author = UserNameSerializer(read_only=True)

    class Meta:
        model = m.News
        fields = (
            'id', 'title', 'author', 'is_published', 
        )


class NewsAdminSerializer(serializers.ModelSerializer):
    """News Serializer for web manager
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

    def create(self, validated_data):
        audiences = self.context.get('audiences', [])
        news = m.News.objects.create(
            author=get_object_or_404(m.User, id=self.context.get('author')),
            **validated_data
        )

        batch_size = 100
        objs = (
            m.NewsAudiences(
                news=news, audience=get_object_or_404(m.User, id=audience)
            ) for audience in audiences
        )
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.NewsAudiences.objects.bulk_create(batch, batch_size)

        return news

    def update(self, instance, validated_data):
        audiences = self.context.get('audiences', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.author = get_object_or_404(m.User, id=self.context.get('author'))
        instance.save()

        instance.newsaudiences_set.exclude(audience__in=audiences).delete()
        existing_audiences = instance.audiences.values_list('id', flat=True)
        new_audiences = [audience for audience in audiences if audience not in existing_audiences]
        batch_size = 100
        objs = (
            m.NewsAudiences(
                news=news, audience=get_object_or_404(m.User, id=audience)
            ) for audience in new_audiences
        )
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            m.NewsAudiences.objects.bulk_create(batch, batch_size)

        return instance


class NewsAudiencesAppSerializer(serializers.ModelSerializer):
    """NewsAudience Serializer for app
    """
    read_on = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    news = NewsBodylessSerializer()

    class Meta:
        model = m.NewsAudiences
        fields = (
            'news', 'is_read', 'read_on'
        )


class NotificationsSerializer(serializers.ModelSerializer):

    author = UserNameSerializer(read_only=True)
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )
    updated = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False
    )

    class Meta:
        model = m.Notifications
        fields = '__all__'

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
