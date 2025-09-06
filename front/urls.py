from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('search/', search_page, name='search_page'),
    path('products', products_page, name='products_page'),
    path('product/<int:product_id>/', product_page,  name='product_page'),
    path('product/<int:product_id>/refetch/', refetch_product, name='refetch_product'),
    path('stores', stores_list, name='stores_list'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path("cart/remove/<int:item_id>/",  remove_cart_item, name="remove_cart_item"),
    path('cart/', cart_page, name='cart_page'),
    path("checkout/", checkout_page, name="checkout_page"),
    path('place-order/', place_order, name='place_order'),
    path('profile', profile, name='profile'),
    path('update_profile/', update_profile, name='update_profile'),
    path('orders', orders, name='orders'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/complete_payment/', complete_payment, name='complete_payment'),
    path('wallet', wallet, name='wallet'),
    path('wallet/deposit', deposit_money, name='deposit_money'),
    path('transaction-success/', transaction_success, name='transaction_success'),
    path('support', support, name='support'),
    path('support/create/', create_ticket, name='create_ticket'),
    path('login/', login_view, name='login'),
    path('verify-otp/<str:phone>/', verify_otp, name='verify_otp'),
    path('about', about_page, name='about_page'),
    path('contact', contact_page, name='contact_page'),
    path('logout/', logout_confirmation, name='logout_confirmation'),
    path('logout/confirm/', logout_view, name='logout'),
]
