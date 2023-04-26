from rest_framework import serializers
from .models import Cart, MenuItem, Category, Order, OrderItem
from decimal import Decimal
from django.contrib.auth.models import User


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["menuitem", "quantity", "unit_price", "price"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = Order
        fields = ["user", "orderitems", "status", "total", "date"]
        depth = 1


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["menuitem", "quantity"]
        depth = 1


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    price_after_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "price",
            "featured",
            "price_after_tax",
            "category",
            "category_id",
        ]

    def calculate_tax(self, product: MenuItem):
        return product.price * Decimal(1.1)
