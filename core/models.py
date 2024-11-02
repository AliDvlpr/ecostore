import random
from datetime import datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError('The phone field must be set')
        
        user = self.model(phone=phone,username=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if phone is None:
            raise ValueError('The phone field must be set for superuser.')

        return self._create_user(phone, password, **extra_fields)

# Replaced user model with default one to allow customization of User model
class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name='موبایل')
    otp = models.CharField(max_length=5, null=True, blank=True)
    user_code = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name='کد کاربری')

    objects = CustomUserManager() 

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone
    
    def save(self, *args, **kwargs):
        if not self.user_code:
            fixed_number = "8082"
            date_of_join = datetime.now().strftime("%Y%m%d")
            
            # Count the number of users created today
            today_users_count = User.objects.filter(date_joined__date=datetime.now().date()).count()
            daily_counter = today_users_count + 1

            self.user_code = f"{fixed_number}{date_of_join}{daily_counter:03d}"
        super().save(*args, **kwargs)

class Ticket(models.Model):
    STATUS_WAITING = 'W'
    STATUS_ANSWERED = 'A'
    STATUS_CLOSED = 'C'
    STATUS_CHOICES = [
        (STATUS_WAITING, 'Waiting'),
        (STATUS_ANSWERED, 'Answered'),
        (STATUS_CLOSED, 'Closed'),
    ]

    order = models.ForeignKey('store.Order', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False, verbose_name='کاربر')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='W')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title