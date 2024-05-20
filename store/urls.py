from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('orders', views.OrderViewSet, basename='collections')

orders_router = routers.NestedDefaultRouter(
    router, 'orders', lookup='order')
orders_router.register('invoices', views.OrderInvoiceViewSet)
# URLConf
urlpatterns = router.urls + orders_router.urls