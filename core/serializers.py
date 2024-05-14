from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'phone', 'username', 'password', 'first_name', 'last_name', 'is_staff']

class UserSerializer(BaseUserSerializer):
    is_staff = serializers.BooleanField(read_only = True)
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'phone', 'first_name', 'last_name', 'email', 'is_staff']