from django import forms 
from django.contrib import admin
from django.forms import Textarea
from .models import *
from bot import send_telegram_message
import jdatetime
# Register your models here.
class WalletInlineForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = '__all__'

class WalletInline(admin.StackedInline):
    model = Wallet
    form = WalletInlineForm
    fields = ('amount',)
    readonly_fields = ('amount',)
    extra = 0

class OrderInline(admin.TabularInline):  # or admin.StackedInline
    model = Order
    extra = 0
    readonly_fields = ['link_button', 'size', 'color', 'quantity','description', 'customer']
    exclude = ['link']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'get_phone_number', 'order_count')
    list_per_page = 20
    search_fields = ['name']
    inlines = [OrderInline, WalletInline]
    readonly_fields = ['telegram_id']  # make 'telegram_id' read-only

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'اسم'

    def get_phone_number(self, obj):
        return obj.user.phone if obj.user else None

    get_phone_number.short_description = 'شماره موبایل'


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('get_amount', 'customer_name')
    readonly_fields = ('get_amount', 'customer_name')
    search_fields = ('customer_name',)
    exclude=('amount', 'customer')



    def get_amount(self, obj):
        return f"{obj.amount:,} تومان"
    get_amount.short_description = 'موجودی'

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else None
    
    customer_name.short_description = 'مشتری'

class OrderInvoiceForm(forms.ModelForm):
    class Meta:
        model = OrderInvoice
        fields = '__all__'

class OrderInvoiceInline(admin.TabularInline):
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

    

class OrderStatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('get_description', 'link_button', 'get_size', 'get_color', 'get_quantity', 'get_customer', 'last_status')
    readonly_fields = ['description', 'link_button', 'size', 'color' ,'customer']
    exclude = ['link']
    search_fields = ('customer__name', 'description')
    inlines = [OrderInvoiceInline ,OrderStatusInline]

    def get_description(self, obj):
        return obj.description
    get_description.short_description = 'توضیحات'

    def get_size(self, obj):
        return obj.size
    get_size.short_description = 'سایز'

    def get_color(self, obj):
        return obj.color
    get_color.short_description = 'رنگ'

    def get_quantity(self, obj):
        return obj.quantity
    get_quantity.short_description = 'تعداد'

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
class TransactionAdmin(admin.ModelAdmin):
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

