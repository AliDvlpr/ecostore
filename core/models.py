from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

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

    objects = CustomUserManager() 

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone
    

try:
    user = User.objects.get(phone='1111')
    # User exists
except User.DoesNotExist:
    # User does not exist
    # Create a superuser with phone number 1111 and 'password' as the password
    User.objects.create_superuser(phone='1111', password='password')