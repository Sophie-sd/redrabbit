from django.contrib import admin
from .models import Category, Product, ProductImage, ProductAttribute


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Адміністрування категорій"""
    
    list_display = ['name', 'parent', 'is_active', 'sort_order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'sort_order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Адміністрування товарів"""
    
    list_display = [
        'name', 'category', 'retail_price', 'wholesale_price', 
        'is_sale', 'is_active', 'is_featured', 'stock'
    ]
    list_filter = ['is_active', 'is_sale', 'is_featured', 'category']
    search_fields = ['name', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_sale', 'is_featured']
    
    inlines = [ProductImageInline, ProductAttributeInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'category', 'description', 'sku')
        }),
        ('Ціни', {
            'fields': (
                'retail_price', 'wholesale_price', 
                'is_sale', 'sale_price',
                'min_quantity_discount', 'quantity_discount_price'
            )
        }),
        ('Склад та статус', {
            'fields': ('stock', 'is_active', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
