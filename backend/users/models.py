from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q, F
from django.utils.translation import gettext_lazy as _


class Profile(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email = models.EmailField(
        _('email address'),
        blank=False,
        unique=True,
        max_length=254
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username


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
