from django.contrib import admin
from .models import MenuItem, Category, Order, OrderItem

# Register your models here.
admin.site.register((MenuItem, Category, Order, OrderItem))
