from django.db import models


class CreatedTimeModel(models.Model):
    """Create time model

    Used as base class for models needing create time
    """
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Timestamp Model

    Used as base class for models needing timestamp
    """
    created = models.DateTimeField(
        auto_now_add=True
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True
        ordering = (
            '-updated',
        )
