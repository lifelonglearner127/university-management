from django.db import models

from ..accounts.models import User


class Department(models.Model):
    """Teacher Department model
    """
    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        null=True,
        blank=True,
    )


class Profile(models.Model):
    """Teacher profile model
    """
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER = (
        (GENDER_MALE, '男'),
        (GENDER_FEMALE, '女'),
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER,
        default=GENDER_MALE
    )

    avatar = models.ImageField(
        null=True,
        blank=True
    )
