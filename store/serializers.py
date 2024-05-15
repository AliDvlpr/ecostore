from rest_framework import serializers
from core.serializers import UserSerializer
from .models import *

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer( read_only=True)
    class Meta:
        model = Customer
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['link', 'size', 'color', 'description']