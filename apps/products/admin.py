from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import Category, Product, ProductReview, Brand
from .models_sales import Sale


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


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'get_discount_display', 'get_affected_count',
        'get_period', 'get_status', 'is_active'
    ]
    list_filter = ['is_active', 'discount_type', 'start_date', 'end_date']
    search_fields = ['name']
    filter_horizontal = ['categories', 'products']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'is_active')
        }),
        ('Умови знижки', {
            'fields': (
                ('discount_type', 'discount_value'),
            ),
            'description': 'Оберіть тип знижки: відсоток або фіксована сума'
        }),
        ('Застосування знижки', {
            'fields': (
                'categories',
                'products',
            ),
            'description': 'Оберіть категорії (включаючи підкатегорії) та/або конкретні товари'
        }),
        ('Термін дії', {
            'fields': (
                ('start_date', 'end_date'),
            ),
        }),
    )
    
    actions = ['activate_sales', 'deactivate_sales', 'apply_now']
    
    def get_discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return format_html('<strong style="color: #ff4444;">-{}%</strong>', obj.discount_value)
        return format_html('<strong style="color: #ff4444;">-{} ₴</strong>', obj.discount_value)
    get_discount_display.short_description = 'Знижка'
    
    def get_affected_count(self, obj):
        try:
            products = obj.get_affected_products()
            cat_count = obj.categories.count()
            prod_count = obj.products.count()
            return format_html(
                '<span style="color: #666;">Категорій: {}<br>Товарів: {} → <strong>{}</strong> в акції</span>',
                cat_count, prod_count, len(products)
            )
        except:
            return '—'
    get_affected_count.short_description = 'Охоплення'
    
    def get_period(self, obj):
        start = obj.start_date.strftime('%d.%m.%Y %H:%M')
        end = obj.end_date.strftime('%d.%m.%Y %H:%M')
        return format_html('<small>{}<br>до<br>{}</small>', start, end)
    get_period.short_description = 'Період'
    
    def get_status(self, obj):
        if obj.is_active_now():
            return format_html('<span style="color: #4CAF50; font-weight: 600;">🔥 Активна</span>')
        elif obj.is_active and obj.start_date > timezone.now():
            return format_html('<span style="color: #2196F3;">⏰ Очікує</span>')
        elif obj.is_active and obj.end_date < timezone.now():
            return format_html('<span style="color: #ff9800;">⌛ Завершена</span>')
        else:
            return format_html('<span style="color: #999;">✗ Вимкнена</span>')
    get_status.short_description = 'Статус'
    
    def activate_sales(self, request, queryset):
        for sale in queryset:
            sale.is_active = True
            sale.save()
        self.message_user(request, f"Активовано {queryset.count()} акцій", messages.SUCCESS)
    activate_sales.short_description = "✓ Активувати"
    
    def deactivate_sales(self, request, queryset):
        for sale in queryset:
            sale.is_active = False
            sale.save()
        self.message_user(request, f"Деактивовано {queryset.count()} акцій", messages.SUCCESS)
    deactivate_sales.short_description = "✗ Деактивувати"
    
    def apply_now(self, request, queryset):
        for sale in queryset:
            sale.apply_to_products()
        self.message_user(request, f"Застосовано {queryset.count()} акцій до товарів", messages.SUCCESS)
    apply_now.short_description = "🔄 Застосувати зараз"
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_active:
            obj.apply_to_products()
            count = len(obj.get_affected_products())
            self.message_user(request, f"Акцію застосовано до {count} товарів", messages.SUCCESS)


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
