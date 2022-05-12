from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from pinax.models import Painting
from rest_framework_simplejwt.tokens import RefreshToken


class UserAccountManager(BaseUserManager):
    def create_user(self, email, user_name, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name, **extra_fields)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, user_name, password, **extra_fields):

        if password is None:
            raise TypeError('Superusers must have a password.')

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_editor', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name, password, **extra_fields)


class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    user_name = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    favourites = models.ManyToManyField(Painting, related_name='account', blank=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']

    def get_full_name(self):
        return self.first_name

    def __str__(self):
        return self.email

    def get_token(self):
        token = RefreshToken.for_user(self)
        return{
            'refresh_token': str(token),
            'access_token': str(token.access_token)
            }


class Comment(models.Model):
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='comment')
    author = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='comment_user')
    body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.painting.title, self.name)

    class Meta:
        ordering = ('date_added',)
