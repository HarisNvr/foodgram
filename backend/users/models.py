from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _


class Profile(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=False
    )
    email = models.EmailField(
        _('email address'),
        blank=False,
        unique=True,
        max_length=254
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        ordering = ['-id']
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
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'подписку'
        verbose_name_plural = 'Подписки'
