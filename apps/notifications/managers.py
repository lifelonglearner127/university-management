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


class AvailableNotificationsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
        )


class DeletedNotificationsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=True,
        )


class SentNotificationsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
            status='S'
        )


class PendingNotificationsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_deleted=False,
            status='P'
        )
