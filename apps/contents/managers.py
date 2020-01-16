from django.db import models


class AvailableNewsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
        )


class DeletedNewsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=True,
        )


class PublishedNewsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
            is_published=True,
        )


class PendingNewsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
            is_published=False
        )


class AvailableNotificationManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
        )


class DeletedNotificationManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=True,
        )


class SentNotificationManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
            is_sent=True
        )


class PendingNotificationManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
            is_sent=False
        )
