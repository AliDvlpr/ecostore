from django.db import models
from django.utils.html import format_html
from django.conf import settings
from django.db import models
from uuid import uuid4
from core.models import User

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True, verbose_name='اسم')
    telegram_id = models.CharField(max_length=100, null=False, blank=False, verbose_name='کد تلگرام')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='کاربر')

    def __str__(self):
        return self.name or str(self.user.user_code)
    
    class Meta:
        verbose_name_plural = "مشتریان"

    def order_count(self):
        return self.order_set.count()

    order_count.short_description = 'تعداد سفارشات'

class Wallet(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='موجودی')
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="wallet", verbose_name='مشتری')

    def __str__(self):
        return f"کیف پول {self.customer.name}"
    
    class Meta:
        verbose_name_plural = "کیف پول ها"

from django.db import models

class Product(models.Model):
    link = models.URLField(max_length=1000, help_text='Enter the product link', verbose_name='لینک')
    title = models.CharField(max_length=100, null=False, blank=False, verbose_name="عنوان")
    is_public = models.BooleanField(default=False, help_text='Is this a public product?', verbose_name='وضعیت در سایت')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='کاربر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')
    
    class Meta:
        verbose_name_plural = "محصولات"
    
    def link_button(self):
        return format_html("<a href='{}' class='button'>Open Link</a>", self.link)
    link_button.short_description = 'لینک'

class ProductDetails(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="details", verbose_name="محصول")
    description = models.TextField(verbose_name="توضیحات")
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قیمت")
    color = models.CharField(max_length=50, verbose_name="رنگ", null=True, blank=True)
    size = models.CharField(max_length=50, verbose_name="اندازه", null=True, blank=True)
    image_url = models.URLField(max_length=1000, verbose_name="آدرس تصویر", null=True, blank=True)
    availability = models.BooleanField(default=True, verbose_name='موجودی')
    
    def __str__(self):
        return f"{self.product.title} - {self.unit_price}"

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [['cart', 'product']]

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [['cart', 'product']]

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='مشتری')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    def __str__(self):
        return f"Order for {self.customer} at {self.created_at}"

    class Meta:
        verbose_name_plural = "سفارشات"
        permissions = [
            ('cancel_order','Can cancel order')
        ]

class OrderStatus(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status', verbose_name='سفارش')
    STATUS_PENDING = 'P'
    STATUS_ACCEPTED = 'A'
    STATUS_COMPLETE = 'C'
    STATUS_FAILED = 'F'
    STATUS_SENDING = 'S'
    STATUS_RECEIVED = 'R'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار'),
        (STATUS_ACCEPTED, 'تایید شده'),
        (STATUS_COMPLETE, 'پرداخت شده'),
        (STATUS_FAILED, 'لغو شده'),
        (STATUS_SENDING, 'ارسال شده'),
        (STATUS_RECEIVED, 'دریافت شده')
    ]
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='وضعیت')
    status_change = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تغییر')

    class Meta:
        verbose_name_plural = "وضعیت سفارش"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قیمت")

class OrderInvoice(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    STATUS_PENDING = 'P'
    STATUS_CONFIRMED = 'C'
    STATUS_REJECTED = 'R'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_REJECTED, 'Rejected')
    ]
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    description = models.TextField(help_text='Enter the product description', null=True, blank=True)
    photo = models.ImageField(upload_to='invoice/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "صورت حساب ها"

class Transaction(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='مقدار')
    STATUS_PENDING = 'P'
    STATUS_CONFIRMED = 'C'
    STATUS_REJECTED = 'R'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_REJECTED, 'Rejected')
    ]
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='وضعیت')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=False, blank=True, verbose_name='کیف پول')
    photo = models.ImageField(upload_to='receipts/', null=True, blank=True, verbose_name='رسید')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name_plural = "واریز پول"