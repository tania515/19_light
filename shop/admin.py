from django.contrib import admin
from .models import Category, Product, Person, Order


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('fio', 'email')
    list_filter = ["created_at", 'email']


@admin.register(Category)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ['name']


@admin.register(Product)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'category')
    list_filter = ["name", 'category']
    search_fields = ('name', 'category')


@admin.register(Order)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('owner', 'status', 'total')
    list_filter = ["owner", 'status']
    search_fields = ('owner', 'status')

