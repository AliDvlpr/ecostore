import random
from datetime import datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string

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
    phone = models.CharField(max_length=20, unique=True, null=False, blank=False)
    otp = models.CharField(max_length=5, null=True, blank=True)
    user_code = models.CharField(max_length=15, unique=True, null=True, blank=True)

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