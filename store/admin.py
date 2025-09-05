from django import forms 
from django.contrib import admin
from unfold.admin import StackedInline, TabularInline, ModelAdmin
from django.forms import Textarea
from .models import *
import jdatetime
import qrcode
from io import BytesIO
from django.utils.safestring import mark_safe
import base64
# Register your models here.
class WalletInlineForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = '__all__'

class WalletInline(StackedInline):
    model = Wallet
    form = WalletInlineForm
    fields = ('amount',)
    readonly_fields = ('amount',)
    extra = 0

class OrderInline(TabularInline):  # or admin.StackedInline
    model = Order
    extra = 0
    # readonly_fields = ['link_button', 'size', 'color', 'quantity','description', 'customer']
    # exclude = ['link']
    readonly_fields = ['customer']

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ('get_code', 'get_name', 'get_phone_number', 'order_count', 'display_qr_code')
    list_per_page = 20
    search_fields = ['name']
    inlines = [OrderInline, WalletInline]
    readonly_fields = ['telegram_id']  # make 'telegram_id' read-only

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'اسم'

    def get_phone_number(self, obj):
        return obj.user.phone if obj.user else None

    get_phone_number.short_description = 'موبایل'

    def get_code(self, obj):
        return obj.user.user_code if obj.user else None
    
    get_code.short_description = 'کد کاربری'
    
    def display_qr_code(self, obj):
        if obj.user:
            if obj.user.user_code:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(obj.user.user_code)
                qr.make(fit=True)

                img = qr.make_image(fill='black', back_color='white')
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
                return mark_safe(f'<img style="border-radius:10px;" id="qr-code-img" src="data:image/png;base64,{img_str}" width="150" height="150" />')
            return "No QR Code"
        return None



@admin.register(Wallet)
class WalletAdmin(ModelAdmin):
    list_display = ('get_amount', 'customer')
    readonly_fields = ('get_amount', 'customer')
    search_fields = ('customer',)
    exclude=('amount',)



    def get_amount(self, obj):
        return f"{obj.amount:,} تومان"
    get_amount.short_description = 'موجودی'

class OrderInvoiceForm(forms.ModelForm):
    class Meta:
        model = OrderInvoice
        fields = '__all__'

class OrderInvoiceInline(TabularInline):
    model = OrderInvoice
    form = OrderInvoiceForm
    fields = ('description', 'amount', 'photo','status')
    readonly_fields = ('status',)
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "wallet":
            order_id = request.resolver_match.kwargs.get('object_id')
            if order_id:
                order = Order.objects.get(pk=order_id)
                kwargs["queryset"] = Wallet.objects.filter(customer=order.customer)
            else:
                kwargs["queryset"] = Wallet.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    

class OrderStatusInline(TabularInline):
    model = OrderStatus
    extra = 0

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('get_customer', 'last_status')
    search_fields = ('customer__name', 'description')
    inlines = [OrderInvoiceInline ,OrderStatusInline]

    # def get_size(self, obj):
    #     return obj.size
    # get_size.short_description = 'سایز'

    # def get_color(self, obj):
    #     return obj.color
    # get_color.short_description = 'رنگ'

    def get_customer(self, obj):
        return obj.customer
    get_customer.short_description = 'مشتری'

    def last_status(self, obj):
        try:
            # Get the latest status for this order
            statuses = OrderStatus.objects.filter(order=obj).order_by('-status_change').first()
            if statuses:
                # Use get_status_display() to get the human-readable value of the status
                return statuses.get_status_display()
            else:
                return "No status found"
        except OrderStatus.DoesNotExist:
            return "No status found"
        
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        
        # Check if we're dealing with the OrderInvoiceInline formset
        if formset.model == OrderInvoice:
            order = form.instance
            # Check if this is the first invoice for the order
            if not OrderInvoice.objects.filter(order=order).exists():
                # Create a new OrderStatus instance with status 'A' ('تایید شده')
                OrderStatus.objects.create(order=order, status='A')

                # Check if the customer has a telegram_id
                if order.customer.telegram_id:
                    # Construct the message you want to send
                    message = f"سلام، {order.customer.name}, سفارش شما با کد {order.pk} تایید شده است. جهت پرداخت میتوانید اطلاعات سفارش مورد نظر را چک کنید"
                    # Call the function to send the message
        
        # Save the instances
        for instance in instances:
            instance.save()
        formset.save_m2m()

    last_status.short_description = 'آخرین وضعیت'

@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ('get_amount', 'get_status', 'get_wallet','get_date')
    list_filter = ('status',)
    search_fields = ('customer__name',)  # You can customize this based on your requirements

    def get_amount(self, obj):
        return f"{obj.amount:,} تومان"
    get_amount.short_description = 'میزان واریز'

    def get_wallet(self, obj):
        return obj.wallet
    get_wallet.short_description = 'کیف پول'

    def get_status(self, obj):
        return obj.status
    get_status.short_description = 'وضعیت'

    def get_date(self, obj):
        # Assuming 'created_at' is a DateTimeField
        persian_date = jdatetime.date.fromgregorian(date=obj.created_at)
        persian_time = obj.created_at.strftime("%H:%M")  # Format time as HH:MM
        return format_html("تاریخ {} - ساعت {}", persian_date.strftime("%Y/%m/%d"), persian_time)
    get_date.short_description = 'تاریخ ایجاد'

    # If you want to display read-only fields in the admin
    readonly_fields = ('created_at',)

    # Customize ordering if needed
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        if obj.status == Transaction.STATUS_CONFIRMED and change:
            if obj.wallet:
                obj.wallet.amount += obj.amount
                obj.wallet.save()
            else:
                pass

        super().save_model(request, obj, form, change)

from django.contrib import admin
from .models import Product, ProductDetails


class ProductDetailsInline(admin.StackedInline):  # or TabularInline if you prefer
    model = ProductDetails
    extra = 0
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "asin_button", "created_at")
    search_fields = ("title", "asin")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    inlines = [ProductDetailsInline]

    # # Custom column to show "Update" button
    # def update_button(self, obj):
    #     return format_html(
    #         '<a class="button" href="{}">Update</a>',
    #         f"/admin/update-product/{obj.asin}/"
    #     )
    # update_button.short_description = "Update Product"
    # update_button.allow_tags = True

class StoreProductInline(admin.TabularInline):
    model = StoreProduct
    extra = 0  # don't show extra blank rows by default
    autocomplete_fields = ("product",)  # makes it easier to select products if many exist
    readonly_fields = ("created_at",)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "score", "phone", "website", "created_at")
    search_fields = ("name", "owner__username", "phone")
    list_filter = ("score",)
    ordering = ("-score", "name")
    readonly_fields = ("created_at",)
    inlines = [StoreProductInline]  # inline StoreProduct inside Store

@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = ("product", "store", "price", "stock", "url", "created_at")
    search_fields = ("product__title", "store__name")
    list_filter = ("stock",)
    autocomplete_fields = ("product", "store")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)