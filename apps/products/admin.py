from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Category, Product, ProductReview, Brand


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['get_category_image', 'name', 'parent', 'get_products_count', 'is_active', 'sort_order']
    list_display_links = ['get_category_image', 'name']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'external_id']
    list_editable = ['is_active', 'sort_order']
    ordering = ['sort_order', 'name']
    readonly_fields = ['external_id']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'parent', 'image')
        }),
        ('Налаштування', {
            'fields': (('is_active', 'sort_order'),)
        }),
        ('Інформація', {
            'fields': ('external_id',),
            'classes': ('collapse',),
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
        'get_price_display', 'get_badges', 'updated_at'
    ]
    list_display_links = ['get_product_image', 'name']
    list_filter = ['category', 'is_sale', 'is_top', 'is_new', 'updated_at']
    search_fields = ['name', 'sku', 'external_id', 'vendor_name']
    ordering = ['sort_order', '-updated_at']
    date_hierarchy = 'updated_at'
    list_per_page = 50
    
    fieldsets = (
        ('Товар', {
            'fields': ('name', 'category', 'sku')
        }),
        ('Акційна ціна', {
            'fields': (('retail_price', 'sale_price'),),
            'description': 'Встановіть sale_price щоб товар з\'явився в акціях'
        }),
        ('Мітки', {
            'fields': (('is_top', 'is_new'), 'is_featured', 'sort_order'),
            'description': 'is_top - ХІТ ПРОДАЖ, is_new - НОВИНКА, is_featured - показувати в рекомендованих'
        }),
    )
    
    readonly_fields = ['name', 'category', 'sku', 'retail_price']
    
    actions = [
        'mark_as_sale',
        'remove_from_sale',
        'mark_as_top',
        'unmark_as_top',
        'mark_as_new',
        'unmark_as_new',
    ]
    
    def get_product_image(self, obj):
        main_image = obj.images.filter(is_main=True).first() or obj.images.first()
        if main_image:
            return format_html('<img src="{}" class="admin-thumbnail-small" />', main_image.get_image_url())
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
    
    def get_badges(self, obj):
        stickers = obj.get_stickers()
        if not stickers:
            return '—'
        
        badges_html = []
        for sticker in stickers:
            badges_html.append(f'<span class="badge {sticker["class"]}">{sticker["text"]}</span>')
        
        return format_html(' '.join(badges_html))
    get_badges.short_description = 'Бейджі'
    
    def mark_as_sale(self, request, queryset):
        count = 0
        for product in queryset:
            if not product.sale_price:
                continue
            product.is_sale = True
            product.save(update_fields=['is_sale'])
            count += 1
        self.message_user(request, f"Додано в акції: {count} товарів", messages.SUCCESS)
    mark_as_sale.short_description = "🔥 Додати в акції"
    
    def remove_from_sale(self, request, queryset):
        updated = queryset.update(is_sale=False, sale_price=None)
        self.message_user(request, f"Видалено з акцій: {updated} товарів", messages.SUCCESS)
    remove_from_sale.short_description = "Видалити з акцій"
    
    def mark_as_top(self, request, queryset):
        updated = queryset.update(is_top=True)
        self.message_user(request, f"Позначено як ХІТ: {updated} товарів", messages.SUCCESS)
    mark_as_top.short_description = "⭐ Позначити ХІТ ПРОДАЖ"
    
    def unmark_as_top(self, request, queryset):
        updated = queryset.update(is_top=False)
        self.message_user(request, f"Знято ХІТ ПРОДАЖ: {updated} товарів", messages.SUCCESS)
    unmark_as_top.short_description = "Зняти ХІТ ПРОДАЖ"
    
    def mark_as_new(self, request, queryset):
        updated = queryset.update(is_new=True)
        self.message_user(request, f"Позначено НОВИНКА: {updated} товарів", messages.SUCCESS)
    mark_as_new.short_description = "✨ Позначити НОВИНКА"
    
    def unmark_as_new(self, request, queryset):
        updated = queryset.update(is_new=False)
        self.message_user(request, f"Знято НОВИНКА: {updated} товарів", messages.SUCCESS)
    unmark_as_new.short_description = "Зняти НОВИНКА"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').prefetch_related('images')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


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
        ('Відгук', {
            'fields': ('product', 'author_name', 'rating', 'text', 'category_badge')
        }),
        ('Модерація', {
            'fields': ('is_approved',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'Схвалено {updated} відгуків', messages.SUCCESS)
    approve_reviews.short_description = '✓ Схвалити відгуки'
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'Відхилено {updated} відгуків', messages.WARNING)
    disapprove_reviews.short_description = '✗ Відхилити відгуки'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['get_brand_logo', 'name', 'is_active', 'sort_order']
    list_display_links = ['get_brand_logo', 'name']
    list_editable = ['is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['name']
    
    fieldsets = (
        ('Бренд', {
            'fields': ('name', 'slug', 'logo', 'is_active', 'sort_order')
        }),
    )
    
    def get_brand_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" class="admin-thumbnail-small" />', obj.logo.url)
        return format_html('<div class="admin-icon-placeholder">🏷️</div>')
    get_brand_logo.short_description = 'Лого'
