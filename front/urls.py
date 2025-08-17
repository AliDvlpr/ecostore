from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('search/', search_page, name='search_page'),
    path('products', products_page, name='products_page'),
    path('product/<int:product_id>/', product_page,  name='product_page'),
    path('profile', profile, name='profile'),
    path('update_profile/', update_profile, name='update_profile'),
    path('orders', orders, name='orders'),
    path('wallet', wallet, name='wallet'),
    path('wallet/deposit', deposit_money, name='deposit_money'),
    path('transaction-success/', transaction_success, name='transaction_success'),
    path('support', support, name='support'),
    path('support/create/', create_ticket, name='create_ticket'),
    path('login/', login_view, name='login'),
    path('verify-otp/<str:phone>/', verify_otp, name='verify_otp'),
    path('logout/', logout_confirmation, name='logout_confirmation'),
    path('logout/confirm/', logout_view, name='logout'),
]
