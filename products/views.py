from django.shortcuts import render
from rest_framework import viewsets
from . import models, serializers
from rest_framework.decorators import action
from rest_framework.response import Response


# Create your views here.
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.ProductCategorySerializer

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = models.Product.objects.filter(category=category)
        serializers = serializers.ProductSerializer(products, many=True)
        return Response(serializers.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    # filterset_fields = ['category', 'is_active']
    # search_fields = ['name', 'description']
    # ordering_fields = ['created_at', 'price']
    # ordering = ['created_at']