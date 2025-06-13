from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'cart_items', views.CartItemViewSet, basename='cart-item')
urlpatterns = router.urls