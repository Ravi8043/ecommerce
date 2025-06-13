from rest_framework import serializers
from . import models
from products.serializers import ProductSerializer
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only = True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Product.objects.all(),
        source='product',
        write_only=True
    )
    class Meta:
        model = models.CartItem
        fields = ['id','cart', 'product', 'product_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many = True, read_only = True)

    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'items']
        read_only_fields = ['created_at', 'updated_at', 'user']