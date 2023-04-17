from django.contrib import admin
from .models import MenuItem, Category

# Register your models here.
admin.site.register((MenuItem, Category))
