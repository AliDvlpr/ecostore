from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('profile', profile, name='profile'),
    path('login/', login_view, name='login'),
    path('verify-otp/<int:user_id>/', verify_otp, name='verify_otp'),
]
