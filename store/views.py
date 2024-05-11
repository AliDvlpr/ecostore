from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from .models import *
from .serializers import *
# Create your views here.

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

class OrderViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
