from rest_framework import serializers
from .models import MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    stock = serializers.IntegerField(source="inventory")

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "stock"]
