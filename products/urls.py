from rest_framework import routers
from django.urls import path
from . import views
router = routers.DefaultRouter()

router.register(r'categories', views.ProductCategoryViewSet, basename='product-category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'order-items', views.OrderItemViewSet, basename='order-item')
urlpatterns = router.urls