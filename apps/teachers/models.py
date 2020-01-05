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


class TeacherProfile(models.Model):
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
        on_delete=models.CASCADE,
        related_name='profile'
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
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

    def __str__(self):
        return f"{self.user.name}'s profile"


def image_path(instance, filename):
    return f"{instance.teacher.user.username}/{filename}"


class TeacherImage(models.Model):

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to=image_path)
