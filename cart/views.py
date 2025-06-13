from django.shortcuts import render
from rest_framework import viewsets
from . import models, serializers
from django.contrib.auth.models import User
from typing import Any

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
        return models.CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer: serializers.CartItemSerializer):
        serializer.save(cart=self.request.user)