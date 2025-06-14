from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from django.db.models import QuerySet

class ProductCategory(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name
    
class Product(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product_name} - {self.category.category_name}"

class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.zip_code}, {self.country}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipping_addresses'
    )
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_addresses'
    )
# Type hints for reverse relationships (helps with IDE support)
    if TYPE_CHECKING:
        order_items: 'QuerySet[OrderItem]'
    def __str__(self):
        return f"Order {self.user.username} - {self.status}"
    def calculate_total(self):
        # Method 1: Using getattr (safest for type checkers)
        order_items = getattr(self, 'order_items')
        return sum(
            item.price * item.quantity 
            for item in order_items.all()
        ) or Decimal('0.00')
    def save(self, *args, **kwargs):
        """Override save to auto-calculate total_amount"""
        super().save(*args, **kwargs)
        # Only update total_amount if order items exist
        if hasattr(self, 'order_items') and self.order_items.exists():
            calculated_total = self.calculate_total()
            if self.total_amount != calculated_total:
                self.total_amount = calculated_total
                super().save(update_fields=['total_amount'])
    
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('order', 'product')
    def __str__(self):
        return f"{self.quantity} of {self.product.product_name} in {self.order.user.username}'s order"
    

    @property
    def item_total(self):
        """Calculate total for this specific item"""
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        """Override save to update order total when item is saved"""
        super().save(*args, **kwargs)
        # Update the order's total amount
        self.order.save()
    
    # Override delete to update order total when item is deleted
    # This is important to ensure the order total is recalculated
    def delete(self, *args, **kwargs) -> Any:
        """Override delete to update order total when item is deleted"""
        order = self.order
        super().delete(*args, **kwargs)
        # Update the order's total amount after deletion
        order.save()