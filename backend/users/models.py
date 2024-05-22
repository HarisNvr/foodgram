from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q, F


class Profile(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLES = (
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (USER, 'User')
    )

    role = models.CharField(
        max_length=9,
        choices=ROLES,
        default=USER,
        verbose_name='Статус'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class Subscription(models.Model):
    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='followings'
    )
    following = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='followers'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following_constraint'
            ),
            CheckConstraint(
                check=~Q(user=F('following')),
                name='self_following_check_constraint'
            )
        ]
