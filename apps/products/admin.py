from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, ProductImage, ProductAttribute, 
    NewProduct, PromotionProduct, ProductTag,
    Brand, ProductGroup, ProductPurpose
)
from .forms import ProductAdminForm


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['get_image_preview', 'image', 'alt_text', 'is_main', 'sort_order']
    readonly_fields = ['get_image_preview']
    classes = ['collapse']
    verbose_name = 'Зображення товару'
    verbose_name_plural = '📷 Зображення товару (перше буде головним)'
    
    def get_image_preview(self, obj):
        """Попередній перегляд зображення"""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return "Немає зображення"
    get_image_preview.short_description = 'Попередній перегляд'


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ['name', 'value', 'sort_order']
    classes = ['collapse']
    verbose_name = 'Характеристика'
    verbose_name_plural = '📝 Характеристики товару (об\'єм, бренд, тип тощо)'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Адміністрування категорій"""
    
    list_display = ['get_category_image', 'name', 'parent', 'get_products_count', 'is_active', 'sort_order']
    list_display_links = ['get_category_image', 'name']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'sort_order']
    ordering = ['sort_order', 'name']
    save_on_top = True
    
    fieldsets = (
        ('📂 Основна інформація', {
            'fields': ('name', 'slug', 'parent', 'image', 'description')
        }),
        ('⚙️ Налаштування', {
            'fields': (('is_active', 'sort_order'),)
        }),
        ('🔍 SEO (необов\'язково)', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def get_category_image(self, obj):
        """Мініатюра зображення категорії"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">📂</div>')
    get_category_image.short_description = 'Фото'
    
    def get_products_count(self, obj):
        """Кількість товарів у категорії"""
        count = obj.product_set.filter(is_active=True).count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    get_products_count.short_description = 'Товарів'
    
    def get_queryset(self, request):
        """Оптимізація запитів"""
        qs = super().get_queryset(request)
        return qs.select_related('parent')


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    """Адміністрування тегів товарів"""
    
    list_display = ['name', 'slug', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Адміністрування товарів"""
    
    form = ProductAdminForm
    
    list_display = [
        'get_product_image', 'name', 'category', 'sku', 
        'get_retail_price_display', 'get_wholesale_price_display',
        'stock', 'get_status_display', 'is_sale', 'is_top', 'is_new'
    ]
    list_display_links = ['get_product_image', 'name']
    list_filter = [
        'is_active',
        'category',
        'is_sale',
        'is_top',
        'is_new',
        'is_featured',
        'created_at',
        'updated_at'
    ]
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_sale', 'is_top', 'is_new']
    ordering = ['sort_order', '-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    save_on_top = True
    
    # Додаємо autocomplete для швидкого пошуку товарів в інших адмінках
    autocomplete_fields = []
    
    inlines = [ProductImageInline, ProductAttributeInline]
    
    fieldsets = (
        ('📋 Основна інформація', {
            'fields': (
                'name',
                'slug',
                'category',
                'sku',
                'description'
            ),
            'description': 'Назва, категорія та опис товару'
        }),
        ('💰 Ціноутворення', {
            'fields': (
                ('retail_price', 'wholesale_price'),
                ('is_sale', 'sale_price'),
                ('price_3_qty', 'price_5_qty'),
            ),
            'description': '<strong>Роздрібна ціна</strong> — для незареєстрованих користувачів<br>'
                          '<strong>Оптова ціна</strong> — для зареєстрованих оптових клієнтів<br>'
                          '<strong>Акційна ціна</strong> — спеціальна ціна при встановленні "Акційний товар"<br>'
                          '<strong>Ціна від 3/5 шт</strong> — знижка при покупці від 3 або 5 штук'
        }),
        ('📦 Склад та наявність', {
            'fields': (
                ('stock', 'is_active'),
                'is_featured'
            ),
            'description': 'Кількість товару на складі та статус активності'
        }),
        ('🏷️ Позначки товару', {
            'fields': (
                ('is_top', 'is_new'),
                'sort_order'
            ),
            'description': '<strong>ТОП</strong> — топовий/популярний товар<br>'
                          '<strong>Новинка</strong> — новий товар<br>'
                          '<strong>Порядок сортування</strong> — чим менше число, тим вище у списку'
        }),
        ('🔍 SEO налаштування (необов\'язково)', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
            'description': 'Налаштування для пошукових систем. Якщо не заповнено — використовується назва товару'
        }),
        ('📅 Системна інформація', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = [
        'activate_products', 
        'deactivate_products',
        'mark_as_sale',
        'unmark_as_sale',
        'mark_as_top',
        'mark_as_new'
    ]
    
    def get_product_image(self, obj):
        """Мініатюра головного зображення товару"""
        main_image = obj.images.filter(is_main=True).first() or obj.images.first()
        if main_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                main_image.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">📦</div>')
    get_product_image.short_description = 'Фото'
    
    def get_retail_price_display(self, obj):
        """Відображення роздрібної ціни"""
        if obj.is_sale and obj.sale_price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{} ₴</span><br>'
                '<strong style="color: #e91e63;">{} ₴</strong>',
                obj.retail_price, obj.sale_price
            )
        return f"{obj.retail_price} ₴"
    get_retail_price_display.short_description = 'Роздріб'
    
    def get_wholesale_price_display(self, obj):
        """Відображення оптової ціни"""
        if obj.wholesale_price:
            return f"{obj.wholesale_price} ₴"
        return "—"
    get_wholesale_price_display.short_description = 'Опт'
    
    def get_status_display(self, obj):
        """Відображення статусу товару"""
        if obj.is_active:
            if obj.stock > 0:
                return format_html('<span style="color: green;">● В наявності</span>')
            else:
                return format_html('<span style="color: orange;">⚠ Немає на складі</span>')
        return format_html('<span style="color: red;">✕ Неактивний</span>')
    get_status_display.short_description = 'Статус'
    
    # Дії (Actions)
    def activate_products(self, request, queryset):
        """Активувати товари"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активовано {updated} товарів")
    activate_products.short_description = "✓ Активувати обрані товари"
    
    def deactivate_products(self, request, queryset):
        """Деактивувати товари"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивовано {updated} товарів")
    deactivate_products.short_description = "✕ Деактивувати обрані товари"
    
    def mark_as_sale(self, request, queryset):
        """Позначити як акційні"""
        updated = queryset.update(is_sale=True)
        self.message_user(request, f"Позначено як акційні: {updated} товарів")
    mark_as_sale.short_description = "🔥 Позначити як АКЦІЙНІ"
    
    def unmark_as_sale(self, request, queryset):
        """Зняти позначку акційний"""
        updated = queryset.update(is_sale=False)
        self.message_user(request, f"Знято позначку акційний: {updated} товарів")
    unmark_as_sale.short_description = "Зняти позначку АКЦІЙНИЙ"
    
    def mark_as_top(self, request, queryset):
        """Позначити як ТОП"""
        updated = queryset.update(is_top=True)
        self.message_user(request, f"Позначено як ТОП: {updated} товарів")
    mark_as_top.short_description = "⭐ Позначити як ТОП"
    
    def mark_as_new(self, request, queryset):
        """Позначити як новинки"""
        updated = queryset.update(is_new=True)
        self.message_user(request, f"Позначено як новинки: {updated} товарів")
    mark_as_new.short_description = "✨ Позначити як НОВИНКИ"
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Налаштування падаючого списку для категорій"""
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(NewProduct)
class NewProductAdmin(admin.ModelAdmin):
    """Адміністрування новинок на головній сторінці"""
    
    list_display = ['product', 'get_is_new_status', 'sort_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name', 'product__sku']
    list_editable = ['sort_order', 'is_active']
    ordering = ['sort_order', '-created_at']
    autocomplete_fields = ['product']
    
    fieldsets = (
        (None, {
            'fields': ('product', 'sort_order', 'is_active'),
            'description': '✨ Додайте товар в блок "Новинки" на головній сторінці. Товар автоматично отримає статус "Новинка".'
        }),
    )
    
    def get_is_new_status(self, obj):
        """Відображення статусу is_new товару"""
        if obj.product.is_new:
            return format_html('<span style="color: green;">✅ Новинка</span>')
        return format_html('<span style="color: red;">❌ Не новинка</span>')
    get_is_new_status.short_description = 'Статус NEW'
    
    def save_model(self, request, obj, form, change):
        """При збереженні встановлюємо is_new=True для товару"""
        super().save_model(request, obj, form, change)
        if not obj.product.is_new:
            obj.product.is_new = True
            obj.product.save(update_fields=['is_new'])
        self.message_user(request, f'✅ Товар "{obj.product.name}" додано в новинки і позначено статусом NEW')
    
    def delete_model(self, request, obj):
        """При видаленні знімаємо is_new з товару"""
        product_name = obj.product.name
        obj.product.is_new = False
        obj.product.save(update_fields=['is_new'])
        super().delete_model(request, obj)
        self.message_user(request, f'❌ Товар "{product_name}" видалено з новинок і знято статус NEW')
    
    def delete_queryset(self, request, queryset):
        """При масовому видаленні знімаємо is_new з товарів"""
        products = [obj.product for obj in queryset]
        for product in products:
            product.is_new = False
            product.save(update_fields=['is_new'])
        count = len(products)
        super().delete_queryset(request, queryset)
        self.message_user(request, f'❌ З {count} товарів знято статус NEW')


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


# ============================================
#              НОВІ МОДЕЛІ ФІЛЬТРІВ          
# ============================================

# Адміністрування брендів
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'products_count', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    list_editable = ('is_active', 'sort_order')
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'logo', 'description')
        }),
        ('Налаштування', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Системна інформація', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def products_count(self, obj):
        return obj.product_set.count()
    products_count.short_description = 'Кількість товарів'


# Адміністрування груп товарів
@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'products_count', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    list_editable = ('is_active', 'sort_order')
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Налаштування', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Системна інформація', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def products_count(self, obj):
        return obj.product_set.count()
    products_count.short_description = 'Кількість товарів'


# Адміністрування призначень
@admin.register(ProductPurpose)
class ProductPurposeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'products_count', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    list_editable = ('is_active', 'sort_order')
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Налаштування', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Системна інформація', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def products_count(self, obj):
        return obj.product_set.count()
    products_count.short_description = 'Кількість товарів'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Налаштування падаючого списку для товарів"""
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(is_active=True).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
