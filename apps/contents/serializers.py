from django.shortcuts import get_object_or_404
from rest_framework import serializers

from . import models as m
from ..core.serializers import TimeStampedSerializer
from ..accounts.serializers import UserNameSerializer


class NewsSerializer(TimeStampedSerializer):

    author = UserNameSerializer(read_only=True)

    class Meta:
        model = m.News
        fields = '__all__'

    def create(self, validated_data):
        return m.News(
            author=get_object_or_404(m.User, id=self.context.get('author')),
            **validated_data
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.author = get_object_or_404(m.User, id=self.context.get('author'))
        instance.save()
        return instance


class NotificationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Notifications
        fields = '__all__'

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
