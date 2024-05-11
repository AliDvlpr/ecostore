from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('orders', views.OrderViewSet, basename='collections')

# URLConf
urlpatterns = router.urls 