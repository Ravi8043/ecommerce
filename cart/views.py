from django.shortcuts import render
from rest_framework import viewsets
from . import models, serializers
from django.contrib.auth.models import User
from typing import Any
from rest_framework.decorators import action
from rest_framework.response import Response

class CartViewSet(viewsets.ModelViewSet):
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer

    def get_queryset(self) -> Any:
        return models.Cart.objects.filter(user = self.request.user)
    
    def perform_create(self, serializer: serializers.CartSerializer):
        serializer.save(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = models.CartItem.objects.all()
    serializer_class = serializers.CartItemSerializer

    def get_queryset(self) -> Any:
        return models.CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer: serializers.CartItemSerializer) -> Any:
    # Get or create a cart for the current user
        cart, created = models.Cart.objects.get_or_create(
        user=self.request.user,
    )
        serializer.save(cart=cart)
    
    @action(detail=False, methods=['post'])
    def add_to_cart(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = models.Product.objects.get(id=product_id)
        cart, created = models.Cart.objects.get_or_create(user=request.user)
        cart_item, created = models.CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        serializer = serializers.CartItemSerializer(cart_item)
        return Response(serializer.data)
    @action(detail=False, methods=['post'])
    def remove_from_cart(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"error": "Product ID is required"}, status=400)
        try:
            product = models.Product.objects.get(id=product_id)
        except models.Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)
        
        # Get the user's cart
        cart, created = models.Cart.objects.get_or_create(user=request.user)
        try:
            cart_item = models.CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=204)
        except models.CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=404)
