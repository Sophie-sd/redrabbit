from django.contrib import admin
from .models import Category, Product, ProductImage, ProductAttribute, RecommendedProduct, PromotionProduct


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'sort_order']


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ['name', 'value', 'sort_order']


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
        'stock', 'is_active', 'is_sale', 'is_top', 'is_new', 'sort_order'
    ]
    list_filter = [
        'is_active',
        'category',
        'is_sale',
        'is_top',
        'is_new',
        'created_at'
    ]
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_sale', 'is_top', 'is_new', 'sort_order']
    ordering = ['sort_order', '-created_at']
    date_hierarchy = 'created_at'
    
    inlines = [ProductImageInline, ProductAttributeInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'category', 'sku', 'description')
        }),
        ('Ціни', {
            'fields': (
                ('retail_price', 'wholesale_price'),
                ('is_sale', 'sale_price'),
                ('price_3_qty', 'price_5_qty')
            ),
            'description': 'Роздрібна ціна — для незареєстрованих. Оптова ціна — для зареєстрованих клієнтів.'
        }),
        ('Стікери', {
            'fields': (
                ('is_top', 'is_new'),
                'sort_order'
            ),
            'description': 'Позначки товару на сайті'
        }),
        ('Наявність', {
            'fields': (('stock', 'is_active'),)
        }),
        ('SEO (необов\'язково)', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Налаштування падаючого списку для категорій"""
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(RecommendedProduct)
class RecommendedProductAdmin(admin.ModelAdmin):
    """Адміністрування рекомендованих товарів на головній сторінці"""
    
    list_display = ['product', 'sort_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name']
    list_editable = ['sort_order', 'is_active']
    ordering = ['sort_order', '-created_at']
    
    def get_queryset(self, request):
        """Обмежуємо список 10 товарами"""
        qs = super().get_queryset(request)
        return qs[:10]
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Налаштування падаючого списку для товарів"""
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(is_active=True).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_add_permission(self, request):
        """Обмежуємо кількість рекомендованих товарів до 10"""
        if RecommendedProduct.objects.count() >= 10:
            return False
        return super().has_add_permission(request)


@admin.register(PromotionProduct)
class PromotionProductAdmin(admin.ModelAdmin):
    """Адміністрування акційних пропозицій на головній сторінці"""
    
    list_display = [
        'product', 
        'get_original_price_display', 
        'discount_price', 
        'get_discount_display',
        'sort_order', 
        'is_active', 
        'updated_at'
    ]
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['product__name', 'product__sku']
    list_editable = ['discount_price', 'sort_order', 'is_active']
    ordering = ['sort_order', '-created_at']
    readonly_fields = ['created_at', 'updated_at', 'get_discount_percentage']
    
    fieldsets = (
        ('Товар', {
            'fields': ('product',)
        }),
        ('Ціни', {
            'fields': (
                'discount_price',
                'get_discount_percentage'
            ),
            'description': 'Оригінальна ціна буде перекреслена на сайті, відображатиметься акційна ціна'
        }),
        ('Налаштування', {
            'fields': ('sort_order', 'is_active')
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_original_price_display(self, obj):
        """Відображення оригінальної ціни"""
        return f"{obj.get_original_price()} ₴"
    get_original_price_display.short_description = 'Оригінальна ціна'
    
    def get_discount_display(self, obj):
        """Відображення знижки у відсотках"""
        percentage = obj.get_discount_percentage()
        return f"-{percentage}%"
    get_discount_display.short_description = 'Знижка'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Налаштування падаючого списку для товарів"""
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(is_active=True).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
