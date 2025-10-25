from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import Category, Product, ProductReview, Brand
from .proxy_models import SaleProduct


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
        'get_price_display', 'get_badges', 'stock'
    ]
    list_display_links = ['get_product_image', 'name']
    list_filter = ['category', 'is_sale', 'is_top', 'is_new']
    search_fields = ['name', 'sku', 'external_id', 'vendor_name']
    ordering = ['sort_order', '-updated_at']
    list_per_page = 50
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'category', 'sku', 'stock')
        }),
        ('Ціноутворення', {
            'fields': ('retail_price',),
        }),
        ('Бейджі', {
            'fields': ('is_top', 'is_new', 'is_featured', 'sort_order'),
            'description': 'is_top - ХІТ ПРОДАЖ, is_new - НОВИНКА'
        }),
    )
    
    readonly_fields = ['name', 'category', 'sku', 'retail_price', 'stock']
    
    actions = [
        'mark_as_top',
        'unmark_as_top',
        'mark_as_new',
        'unmark_as_new',
        'export_products_csv',
    ]
    
    def get_product_image(self, obj):
        main_image = obj.images.filter(is_main=True).first() or obj.images.first()
        if main_image:
            return format_html('<img src="{}" class="admin-thumbnail-small" />', main_image.get_image_url())
        return format_html('<div class="admin-icon-placeholder">📦</div>')
    get_product_image.short_description = 'Фото'
    
    def get_price_display(self, obj):
        if obj.is_sale_active():
            discount = obj.get_discount_percentage()
            return format_html(
                '<div><s style="color: #999;">{} ₴</s><br><strong style="color: #ff4444; font-size: 16px;">{} ₴</strong> <span style="background: #ff4444; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">-{}%</span></div>',
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
    mark_as_new.short_description = "⭐ Позначити НОВИНКА"
    
    def unmark_as_new(self, request, queryset):
        updated = queryset.update(is_new=False)
        self.message_user(request, f"Знято НОВИНКА: {updated} товарів", messages.SUCCESS)
    unmark_as_new.short_description = "Зняти НОВИНКА"
    
    def export_products_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="products_export.csv"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow([
            'SKU', 'Назва', 'Категорія', 'Ціна', 'Акційна ціна',
            'ХІТ', 'Новинка', 'Акція', 'Наявність'
        ])
        
        for product in queryset:
            writer.writerow([
                product.sku,
                product.name,
                product.category.name,
                product.retail_price,
                product.sale_price or '',
                'Так' if product.is_top else 'Ні',
                'Так' if product.is_new else 'Ні',
                'Так' if product.is_sale else 'Ні',
                product.stock,
            ])
        
        self.message_user(request, f"Експортовано {queryset.count()} товарів")
        return response
    export_products_csv.short_description = "📥 Експортувати в CSV"
    
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


@admin.register(SaleProduct)
class SaleProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_product_image', 'name', 'category', 
        'get_original_price', 'get_sale_price_field', 'get_dates', 'get_status'
    ]
    list_display_links = ['get_product_image', 'name']
    list_filter = ['category', 'is_sale', 'sale_start_date', 'sale_end_date']
    search_fields = ['name', 'sku']
    ordering = ['-updated_at']
    list_per_page = 50
    
    fieldsets = (
        ('Товар', {
            'fields': ('name', 'category', 'sku', 'retail_price')
        }),
        ('Акційна пропозиція', {
            'fields': (
                'is_sale',
                'sale_price',
                ('sale_start_date', 'sale_end_date'),
            ),
            'description': 'Встановіть акційну ціну та терміни дії'
        }),
    )
    
    readonly_fields = ['name', 'category', 'sku', 'retail_price']
    
    actions = ['activate_sale', 'deactivate_sale', 'extend_sale']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_active=True).select_related('category').prefetch_related('images')
    
    def get_product_image(self, obj):
        main_image = obj.images.filter(is_main=True).first() or obj.images.first()
        if main_image:
            return format_html('<img src="{}" class="admin-thumbnail-small" />', main_image.get_image_url())
        return format_html('<div class="admin-icon-placeholder">📦</div>')
    get_product_image.short_description = 'Фото'
    
    def get_original_price(self, obj):
        return format_html('<strong>{} ₴</strong>', obj.retail_price)
    get_original_price.short_description = 'Звичайна ціна'
    
    def get_sale_price_field(self, obj):
        if obj.sale_price:
            discount = obj.get_discount_percentage() if obj.is_sale_active() else 0
            if discount > 0:
                return format_html(
                    '<strong style="color: #ff4444; font-size: 16px;">{} ₴</strong><br><span style="background: #ff4444; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">-{}%</span>',
                    obj.sale_price, discount
                )
            return format_html('<strong style="color: #ff4444;">{} ₴</strong>', obj.sale_price)
        return '—'
    get_sale_price_field.short_description = 'Акційна ціна'
    
    def get_dates(self, obj):
        if obj.sale_start_date or obj.sale_end_date:
            start = obj.sale_start_date.strftime('%d.%m.%Y') if obj.sale_start_date else '—'
            end = obj.sale_end_date.strftime('%d.%m.%Y') if obj.sale_end_date else '—'
            return format_html('<small>З: {}<br>До: {}</small>', start, end)
        return '—'
    get_dates.short_description = 'Термін дії'
    
    def get_status(self, obj):
        if obj.is_sale and obj.is_sale_active():
            return format_html('<span style="color: #4CAF50; font-weight: 600;">🔥 Активна</span>')
        elif obj.is_sale and obj.sale_price:
            return format_html('<span style="color: #ff9800;">⏰ Очікує/завершена</span>')
        else:
            return format_html('<span style="color: #999;">✗ Не активна</span>')
    get_status.short_description = 'Статус'
    
    def activate_sale(self, request, queryset):
        updated = 0
        for product in queryset:
            if product.sale_price:
                product.is_sale = True
                product.save(update_fields=['is_sale'])
                updated += 1
        self.message_user(request, f"Активовано {updated} акцій", messages.SUCCESS)
    activate_sale.short_description = "🔥 Активувати акцію"
    
    def deactivate_sale(self, request, queryset):
        updated = queryset.update(is_sale=False)
        self.message_user(request, f"Деактивовано {updated} акцій", messages.SUCCESS)
    deactivate_sale.short_description = "✗ Деактивувати акцію"
    
    def extend_sale(self, request, queryset):
        from datetime import timedelta
        for product in queryset:
            if product.sale_end_date:
                product.sale_end_date += timedelta(days=7)
                product.save(update_fields=['sale_end_date'])
        self.message_user(request, f"Продовжено {queryset.count()} акцій на 7 днів", messages.SUCCESS)
    extend_sale.short_description = "📅 Продовжити на 7 днів"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


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
