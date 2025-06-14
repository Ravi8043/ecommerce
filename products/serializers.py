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

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = ['id', 'user', 'street', 'city', 'state', 'zip_code', 'country']
        read_only_fields = ['user']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only = True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset = models.Product.objects.all(),
        source = 'product',
        write_only = True
    )
    item_price = serializers.SerializerMethodField()
    
    class Meta:
        model = models.OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'created_at', 'updated_at', 'order','product_id']
        read_only_fields = ['created_at', 'updated_at']
    def get_item_price(self, obj):
        return obj.product.price * obj.quantity
    
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    calculated_total = serializers.SerializerMethodField()
    class Meta:
        model = models.Order
        fields = ['id', 'user', 'created_at', 'updated_at', 'total_amount', 'status', 'order_items']
        read_only_fields = ['created_at', 'updated_at', 'user']
    def get_calculated_total(self, obj):
        return obj.calculate_total()

