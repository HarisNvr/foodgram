from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from .constants import NAME_LENGTH, LAST_NAME_LENGTH


class Profile(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    first_name = models.CharField(
        max_length=NAME_LENGTH,
        blank=False
    )
    last_name = models.CharField(
        max_length=LAST_NAME_LENGTH,
        blank=False
    )
    email = models.EmailField(
        blank=False,
        unique=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        ordering = ['first_name', 'last_name', 'username', 'email']
        verbose_name = 'профиль'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='followings'
    )
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='followers'
    )

    class Meta:
        ordering = ['user', 'author']
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'подписку'
        verbose_name_plural = 'Подписки'
