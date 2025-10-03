from django.contrib import admin
from .models import Category, Product, ProductImage, ProductAttribute, ProductTag


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    """Адміністрування тегів товарів"""
    
    list_display = ['name', 'slug', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Адміністрування категорій"""
    
    list_display = ['name', 'parent', 'is_active', 'sort_order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'sort_order']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self, request):
        """Виключаємо видалені категорії"""
        qs = super().get_queryset(request)
        # Можемо додати фільтрацію тут, якщо потрібно
        return qs


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Адміністрування товарів"""
    
    list_display = [
        'name', 'category', 'sku', 'retail_price', 'wholesale_price', 
        'is_top', 'is_new', 'is_sale', 'is_active', 'is_featured', 'stock', 'sort_order'
    ]
    list_filter = [
        'is_active', 'is_sale', 'is_featured', 'is_top', 'is_new', 
        'category', 'tags'
    ]
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_sale', 'is_featured', 'is_top', 'is_new', 'sort_order']
    filter_horizontal = ['tags']
    
    inlines = [ProductImageInline, ProductAttributeInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'category', 'description', 'sku', 'tags')
        }),
        ('Ціни', {
            'fields': (
                ('retail_price', 'wholesale_price'),
                ('is_sale', 'sale_price'),
                ('price_3_qty', 'price_5_qty'),
                ('min_quantity_discount', 'quantity_discount_price')
            )
        }),
        ('Стікери та позиціонування', {
            'fields': (
                ('is_top', 'is_new', 'is_featured'),
                'sort_order'
            )
        }),
        ('Склад та статус', {
            'fields': ('stock', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Налаштування падаючого списку для категорій"""
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
