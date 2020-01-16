from django.db import models


class AvailableAdvertisementManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
        )


class DeletedAdvertisementManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=True,
        )


class PublishedAdvertisementManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
            is_published=True,
        )


class PendingAdvertisementManager(models.Manager):

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
