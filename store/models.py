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

class Product(models.Model):
    asin = models.CharField(max_length=20, unique=True, verbose_name="ASIN")
    title = models.CharField(max_length=250, verbose_name="عنوان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.title

    def asin_button(self):
        return format_html("<span class='badge bg-primary'>{}</span>", self.asin)
    asin_button.short_description = 'ASIN'


class ProductDetails(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="details", verbose_name="محصول")
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    pricing = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="قیمت")
    list_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="قیمت قبل از تخفیف")
    images = models.JSONField(default=list, blank=True, verbose_name="تصاویر")  # List of image URLs
    feature_bullets = models.JSONField(default=list, blank=True, verbose_name="ویژگی‌ها")  # List of bullets
    customization_options = models.JSONField(default=dict, blank=True, verbose_name="گزینه‌های سفارشی")  
    # Example: {"Color": [{"value": "Red", "asin": "B0X...", "image": "..."}, ...], "Edition": [...]}

    def __str__(self):
        return f"{self.product.title} - {self.pricing}"

class Store(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    score = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # e.g. 4.5
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.score})"
    
    class Meta:
        verbose_name_plural = "فروشگاه ها"
    
class StoreProduct(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stores")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.BooleanField(default=True)  # if the store currently has stock
    url = models.URLField(blank=True, null=True)  # direct product link in the store

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('store', 'product')  # prevent duplicate entries

    def __str__(self):
        return f"{self.product.title} at {self.store.name}"

    class Meta:
        verbose_name_plural = "محصولات فروشگاه ها"
    

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store_product = models.ForeignKey(StoreProduct, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = [['cart', 'product', 'store_product']]

    def __str__(self):
        if self.store_product:
            return f"{self.product.title} from {self.store_product.store.name} x {self.quantity}"
        return f"{self.product.title} x {self.quantity}"


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

