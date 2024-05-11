from django import forms 
from django.contrib import admin
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from .models import *
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
    readonly_fields = ['link_button', 'size', 'color', 'description', 'customer']
    exclude = ['link']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_phone_number', 'telegram_id', 'order_count')
    list_per_page = 20
    search_fields = ['name']
    inlines = [OrderInline, WalletInline]
    readonly_fields = ['telegram_id']  # make 'telegram_id' read-only

    def get_phone_number(self, obj):
        return obj.user.phone if obj.user else None

    get_phone_number.short_description = 'Phone Number'

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('amount', 'customer_name')
    readonly_fields = ('amount',)

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else None
    
    customer_name.short_description = 'Customer Name'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('description', 'link_button', 'size', 'color',  'customer')
    readonly_fields = ['description', 'link_button', 'size', 'color', 'customer']
    exclude = ['link']
    search_fields = ('customer__name', 'discription')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount','action', 'status', 'wallet','created_at')
    list_filter = ('action', 'status')
    search_fields = ('customer__name',)  # You can customize this based on your requirements


    # Customize the form fields and layout if needed
    fieldsets = (
        (None, {
            'fields': ('action', 'amount', 'status', 'order', 'wallet','created_at')
        }),
        ('عکس رسید (برای افزایش موجودی کیف پول)', {
            'fields': ('photo',),
            'classes': ('collapse',)  # Optional, collapses this section by default
        }),
    )

    # If you want to display read-only fields in the admin
    readonly_fields = ('action', 'created_at')

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

