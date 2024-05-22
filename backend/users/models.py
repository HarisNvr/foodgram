from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q, F


class ProfileManager(BaseUserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Profile.ADMIN)

        email = self.normalize_email(email)
        superuser = self.model(email=email, **extra_fields)
        superuser.set_password(password)
        superuser.save(using=self._db)
        return superuser


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

    objects = ProfileManager()

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
