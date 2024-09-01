from rest_framework import serializers
from core.serializers import UserSerializer
from .models import *

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer( read_only=True)
    class Meta:
        model = Customer
        fields = '__all__'

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['status', 'status_change']

class OrderInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInvoice
        fields = ['amount', 'status', 'description', 'photo', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    status = OrderStatusSerializer(many=True, read_only=True)
    invoice = OrderInvoiceSerializer(many=True, read_only = True)
    last_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'product', 'quantity', 'description', 'customer', 'created_at', 'invoice','status', 'last_status']

    def get_last_status(self, obj):
        last_status = obj.status.order_by('-status_change').first()
        if last_status:
            return OrderStatusSerializer(last_status).data
        return None

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['product', 'quantity','description']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['link', 'size', 'color']