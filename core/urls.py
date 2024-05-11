from django.urls import path
from rest_framework_nested import routers
from django.urls.conf import include
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify/', views.VerifyView.as_view(), name='verify'),
]