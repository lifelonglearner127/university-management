from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

from ..core.validators import validate_mobile, validate_username


class UserManager(BaseUserManager):
    """Default User Model Manager
    """
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_super_user', True)

        user = self.create_user(
            username,
            password=password,
            name=username,
            **extra_fields
        )

        return user


class User(AbstractBaseUser):
    """User model
    """
    username = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_username]
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    mobile = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_mobile]
    )

    device_token = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    channel_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    last_seen = models.DateTimeField(
        auto_now=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_super_user = models.BooleanField(
        default=False
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_super_user

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_super_user:
            return True

        return False

    def has_module_perms(self, app_label):
        if self.is_active and self.is_super_user:
            return True

        return False
