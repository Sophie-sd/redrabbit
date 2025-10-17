"""
Адміністративна панель товарів
"""
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages

from .models import Category, Product, ProductImage, ProductAttribute, ProductTag, ProductReview, Brand


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['get_image_preview', 'image', 'alt_text', 'is_main', 'sort_order']
    readonly_fields = ['get_image_preview']
    classes = ['collapse']
    verbose_name = 'Зображення товару'
    verbose_name_plural = 'Зображення товару'
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="admin-thumbnail" />', obj.image.url)
        return "Немає зображення"
    get_image_preview.short_description = 'Превью'


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ['name', 'value', 'sort_order']
    classes = ['collapse']
    verbose_name = 'Характеристика'
    verbose_name_plural = 'Характеристики товару'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['get_category_image', 'name', 'parent', 'get_products_count', 'is_active', 'sort_order']
    list_display_links = ['get_category_image', 'name']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description', 'external_id']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'sort_order']
    ordering = ['sort_order', 'name']
    save_on_top = True
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'parent', 'image', 'description')
        }),
        ('Налаштування', {
            'fields': (('is_active', 'sort_order'),)
        }),
        ('Імпорт', {
            'fields': ('external_id',),
            'classes': ('collapse',),
            'description': 'ID категорії в системі постачальника (автоматично)'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def get_category_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="admin-thumbnail-small" />', obj.image.url)
        return format_html('<div class="admin-icon-placeholder">📂</div>')
    get_category_image.short_description = 'Фото'
    
    def get_products_count(self, obj):
        count = obj.product_set.filter(is_active=True).count()
        return format_html('<span class="badge badge-info">{}</span>', count)
    get_products_count.short_description = 'Товарів'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_product_image', 'name', 'category', 'sku', 
        'get_price_display', 'stock', 'get_status_display', 'get_badges', 'updated_at'
    ]
    list_display_links = ['get_product_image', 'name']
    list_filter = [
        'is_active', 'category', 'is_sale', 'is_top', 'is_new', 'is_featured',
        'created_at', 'updated_at'
    ]
    search_fields = ['name', 'sku', 'description', 'external_id', 'vendor_name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['stock']
    ordering = ['sort_order', '-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    save_on_top = True
    
    inlines = [ProductImageInline, ProductAttributeInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'category', 'sku', 'description')
        }),
        ('Ціна', {
            'fields': ('retail_price', ('is_sale', 'sale_price')),
            'description': 'Акційна ціна оновлюється автоматично з файлів постачальника'
        }),
        ('Склад та наявність', {
            'fields': (('stock', 'is_active'), 'is_featured')
        }),
        ('Бейджі (встановлюються вручну)', {
            'fields': (('is_top', 'is_new'), 'sort_order'),
            'description': 'ХІТ та НОВИНКА встановлюються вручну. Бейдж АКЦІЯ з\'являється автоматично при наявності акційної ціни'
        }),
        ('Інформація з імпорту', {
            'fields': ('external_id', 'vendor_name'),
            'classes': ('collapse',),
            'description': 'Дані з файлів постачальника (автоматично)'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Системна інформація', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = [
        'activate_products', 
        'deactivate_products',
        'mark_as_top',
        'unmark_as_top',
        'mark_as_new',
        'unmark_as_new',
        'export_to_csv',
    ]
    
    def get_product_image(self, obj):
        main_image = obj.images.filter(is_main=True).first() or obj.images.first()
        if main_image:
            return format_html('<img src="{}" class="admin-thumbnail-small" />', main_image.image.url)
        return format_html('<div class="admin-icon-placeholder">📦</div>')
    get_product_image.short_description = 'Фото'
    
    def get_price_display(self, obj):
        if obj.is_sale and obj.sale_price:
            discount = obj.get_discount_percentage()
            return format_html(
                '<div><strong>{} ₴</strong><br><span class="badge badge-sale">{} ₴ (-{}%)</span></div>',
                obj.retail_price, obj.sale_price, discount
            )
        return format_html('<strong>{} ₴</strong>', obj.retail_price)
    get_price_display.short_description = 'Ціна'
    
    def get_status_display(self, obj):
        if obj.is_active:
            if obj.stock > 0:
                return format_html('<span class="status-active">● В наявності</span>')
            else:
                return format_html('<span class="status-warning">⚠ Немає на складі</span>')
        return format_html('<span class="status-inactive">✕ Неактивний</span>')
    get_status_display.short_description = 'Статус'
    
    def get_badges(self, obj):
        stickers = obj.get_stickers()
        if not stickers:
            return '—'
        
        badges_html = []
        for sticker in stickers:
            badges_html.append(f'<span class="badge {sticker["class"]}">{sticker["text"]}</span>')
        
        return format_html(' '.join(badges_html))
    get_badges.short_description = 'Бейджі'
    
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активовано {updated} товарів", messages.SUCCESS)
    activate_products.short_description = "✓ Активувати обрані товари"
    
    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивовано {updated} товарів", messages.SUCCESS)
    deactivate_products.short_description = "✕ Деактивувати обрані товари"
    
    def mark_as_top(self, request, queryset):
        updated = queryset.update(is_top=True)
        self.message_user(request, f"Позначено як ХІТ: {updated} товарів", messages.SUCCESS)
    mark_as_top.short_description = "⭐ Позначити як ХІТ"
    
    def unmark_as_top(self, request, queryset):
        updated = queryset.update(is_top=False)
        self.message_user(request, f"Знято позначку ХІТ: {updated} товарів", messages.SUCCESS)
    unmark_as_top.short_description = "Зняти позначку ХІТ"
    
    def mark_as_new(self, request, queryset):
        updated = queryset.update(is_new=True)
        self.message_user(request, f"Позначено як НОВИНКИ: {updated} товарів", messages.SUCCESS)
    mark_as_new.short_description = "✨ Позначити як НОВИНКИ"
    
    def unmark_as_new(self, request, queryset):
        updated = queryset.update(is_new=False)
        self.message_user(request, f"Знято позначку НОВИНКА: {updated} товарів", messages.SUCCESS)
    unmark_as_new.short_description = "Зняти позначку НОВИНКА"
    
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="products_export.csv"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow(['SKU', 'Назва', 'Категорія', 'Ціна', 'Акційна ціна', 'Кількість', 'Статус'])
        
        for product in queryset:
            writer.writerow([
                product.sku,
                product.name,
                product.category.name,
                product.retail_price,
                product.sale_price or '',
                product.stock,
                'Активний' if product.is_active else 'Неактивний'
            ])
        
        self.message_user(request, f"Експортовано {queryset.count()} товарів", messages.SUCCESS)
        return response
    export_to_csv.short_description = "📊 Експортувати в CSV"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').prefetch_related('images')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'author_name', 'rating', 'is_approved', 'created_at']
    list_display_links = ['product', 'author_name']
    list_filter = ['is_approved', 'rating', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['product__name', 'author_name', 'text']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('product', 'author_name', 'rating', 'text')
        }),
        ('Додатково', {
            'fields': ('category_badge', 'is_approved')
        }),
        ('Системна інформація', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'Схвалено {updated} відгуків', messages.SUCCESS)
    approve_reviews.short_description = '✓ Схвалити вибрані відгуки'
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'Відхилено {updated} відгуків', messages.WARNING)
    disapprove_reviews.short_description = '✗ Відхилити вибрані відгуки'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['get_brand_logo', 'name', 'is_active', 'sort_order', 'created_at']
    list_display_links = ['get_brand_logo', 'name']
    list_editable = ['is_active', 'sort_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'logo', 'description')
        }),
        ('Налаштування', {
            'fields': ('is_active', 'sort_order')
        }),
    )
    
    def get_brand_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" class="admin-thumbnail-small" />', obj.logo.url)
        return format_html('<div class="admin-icon-placeholder">🏷️</div>')
    get_brand_logo.short_description = 'Лого'
