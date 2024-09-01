from django.db import models
from django.utils.html import format_html
from django.conf import settings
from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True, verbose_name='اسم')
    telegram_id = models.CharField(max_length=100, null=False, blank=False, verbose_name='کد تلگرام')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='کاربر')

    def __str__(self):
        return self.name or ''
    
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

class Product(models.Model):
    link = models.URLField(help_text='Enter the product link', verbose_name='لینک')
    size = models.CharField(max_length=50, help_text='Enter the product size', verbose_name='سایز')
    color = models.CharField(max_length=50, help_text='Enter the product color', verbose_name='رنگ')
    is_public = models.BooleanField(default=False, help_text='Is this a public product?', verbose_name='وضعیت در سایت')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='مشتری')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name_plural = "محصولات"

    def link_button(self):
        return format_html("<a href='{}' class='button'>Open Link</a>", self.link)

    link_button.short_description = 'لینک'

class Order(models.Model):
    quantity = models.PositiveSmallIntegerField(verbose_name='تعداد')
    description = models.TextField(help_text='Enter the product description', verbose_name='توضیحات')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='مشتری')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    def __str__(self):
        return f"Order for {self.customer} - {self.description}"

    class Meta:
        verbose_name_plural = "سفارشات"

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