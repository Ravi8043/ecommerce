from django.shortcuts import render
from rest_framework import viewsets
from . import models, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from typing import Any
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission, SAFE_METHODS

# Create your views here.
class IsAdminOrReadOnly(BasePermission):
    """
    Allow GET (read-only) for anyone.
    Allow POST/PUT/PATCH/DELETE only for admin/staff.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.ProductCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category_name', 'description']
    ordering_fields = ['category_name', 'created_at']
    ordering = ['created_at']
    permission_classes = [IsAdminOrReadOnly,]

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = models.Product.objects.filter(category=category)
        product_serializer = serializers.ProductSerializer(products, many=True)
        return Response(product_serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product_name', 'description']
    ordering_fields = ['product_name', 'price', 'created_at']
    ordering = ['created_at']
    permission_classes = [IsAdminOrReadOnly,]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self) -> Any:
        return models.Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer: serializers.OrderSerializer):
        order = models.Order.objects.create(user=self.request.user)
        serializer.save(order=order)
 


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = models.OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self) -> Any:
        return models.OrderItem.objects.filter(order__user=self.request.user)
    def perform_create(self, serializer: serializers.OrderItemSerializer) -> Any:
    # Get or create an order for the current user
        order, created = models.Order.objects.get_or_create(
        user=self.request.user,
        defaults={'status': 'pending'}  # or whatever default status you want
    )
        serializer.save(order=order)

    @action(detail=False, methods=['post'])
    def add_to_order(self, request, *args, **kwargs):
        property_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        product = models.Product.objects.get(id=property_id)
        order, created = models.Order.objects.get_or_create(user=request.user)
        order_item, created = models.OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )
        if not created:
            order_item.quantity += quantity
            order_item.save()
        serializer = serializers.OrderItemSerializer(order_item)
        return Response(serializer.data)
    @action(detail=False, methods=['post'])
    def remove_from_order(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"error": "Product ID is required"}, status=400)
        try:
            product = models.Product.objects.get(id=product_id)
        except models.Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)
        
        # Get the user's order
        order, created = models.Order.objects.get_or_create(user=request.user)
        try:
            order_item = models.OrderItem.objects.get(order=order, product=product)
            order_item.delete()
            return Response({"message": "Item removed from order"}, status=204)
        except models.OrderItem.DoesNotExist:
            return Response({"error": "Item not found in order"}, status=404)
    