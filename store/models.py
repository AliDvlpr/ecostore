from django.db import models
from django.utils.html import format_html
from django.conf import settings
from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    telegram_id = models.CharField(max_length=100, unique=True,null=False, blank=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name or ''
    
    class Meta:
        verbose_name_plural = "مشتریان"

    def order_count(self):
        return self.order_set.count()

    order_count.short_description = 'تعداد سفارشات'

class Wallet(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="wallet")

    def __str__(self):
        return f"کیف پول {self.customer.name}"
    
    class Meta:
        verbose_name_plural = "کیف پول ها"

class Order(models.Model):
    link = models.URLField(help_text='Enter the product link')
    size = models.CharField(max_length=50, help_text='Enter the product size')
    color = models.CharField(max_length=50, help_text='Enter the product color')
    description = models.TextField(help_text='Enter the product description')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.customer} - {self.description}"

    class Meta:
        verbose_name_plural = "سفارشات"

    def link_button(self):
        return format_html("<a href='{}' class='button'>Open Link</a>", self.link)

    link_button.short_description = 'لینک'

class OrderStatus(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status')
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
        max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    status_change = models.DateTimeField(auto_now_add=True)

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
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=False, blank=True)
    photo = models.ImageField(upload_to='receipts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "واریز پول"