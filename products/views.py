from django.shortcuts import render
from rest_framework import viewsets
from . import models, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from typing import Any
from rest_framework import filters

# Create your views here.
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.ProductCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category_name', 'description']
    ordering_fields = ['category_name', 'created_at']
    ordering = ['created_at']

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = models.Product.objects.filter(category=category)
        serializers = serializers.ProductSerializer(products, many=True)
        return Response(serializers.data)
    
    

class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product_name', 'description']
    ordering_fields = ['product_name', 'price', 'created_at']
    ordering = ['created_at']



class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

    def get_queryset(self) -> Any:
        return models.Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer: serializers.OrderSerializer):
        serializer.save(user=self.request.user)
    


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = models.OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer

    def get_queryset(self) -> Any:
        return models.OrderItem.objects.filter(user=self.request.user)
    def perform_create(self, serializer: serializers.OrderItemSerializer) -> Any:
        serializer.save(user=self.request.user)
    