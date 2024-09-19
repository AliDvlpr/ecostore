from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.shortcuts import render
from .models import *
from .serializers import *
from .permissions import *
# Create your views here.

class CustomerViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset =Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Customer.objects.all()
        
        return Customer.objects.none()

class ProductViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Show products where the customer is the logged-in user or the product is public
            return Product.objects.filter(customer=user) | Product.objects.filter(is_public=True)
        else:
            # Show only public products for non-logged-in users
            return Product.objects.filter(is_public=True)

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        customer_id = Customer.objects.only(
            'id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)

    def perform_create(self, serializer):
        user = self.request.user
        customer = Customer.objects.get(user_id=user.id)
        order = serializer.save(customer=customer)
        OrderStatus.objects.create(order=order, status=OrderStatus.STATUS_PENDING)


class OrderInvoiceViewSet(ModelViewSet):
    queryset =OrderInvoice.objects.all()
    serializer_class = OrderInvoiceSerializer
    permission_classes = [IsAdminOrReadOnly]

def login_page(request):
    return render(request, 'login.html')