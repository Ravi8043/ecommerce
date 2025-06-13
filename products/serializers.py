from rest_framework import serializers
from . import models

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductCategory
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    stock = serializers.IntegerField(default=0, min_value=0)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset = models.ProductCategory.objects.all(),
        source = 'category',
        write_only = True
    )

    class Meta:
        model = models.Product
        fields = ['id', 'name', 'description', 'price', 
                'category', 'created_at', 'updated_at', 'is_active', 'image', 'stock','category_id']
        read_only_fields = ['created_at', 'updated_at']

