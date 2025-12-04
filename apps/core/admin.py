from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Banner, TrackingPixel


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'desktop_preview', 'mobile_preview', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'alt_text']
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Банер', {
            'fields': ('title', 'alt_text', 'is_active', 'order')
        }),
        ('Зображення', {
            'fields': ('desktop_image', 'mobile_image'),
        }),
        ('Посилання', {
            'fields': ('link_url',),
        }),
    )
    
    def desktop_preview(self, obj):
        if obj.desktop_image:
            return format_html('<img src="{}" alt="{}" class="admin-thumbnail-small" />', obj.desktop_image.url, obj.alt_text)
        return "Немає"
    desktop_preview.short_description = "Десктоп"
    
    def mobile_preview(self, obj):
        if obj.mobile_image:
            return format_html('<img src="{}" alt="{}" class="admin-thumbnail-small" />', obj.mobile_image.url, obj.alt_text)
        return "Немає"
    mobile_preview.short_description = "Мобільний"


class TrackingPixelAdminForm(forms.ModelForm):
    """Форма з вибором сторінок через чекбокси"""
    
    PAGE_CHOICES = [
        ('all', 'Всі сторінки (глобально)'),
        ('home', 'Головна'),
        ('delivery', 'Доставка та оплата'),
        ('returns', 'Повернення та обмін'),
        ('about', 'Про нас'),
        ('contacts', 'Контакти'),
        ('terms', 'Умови використання'),
        ('privacy', 'Політика конфіденційності'),
        ('search', 'Пошук'),
        ('product_list', 'Каталог товарів'),
        ('product_detail', 'Сторінка товару'),
        ('cart', 'Кошик'),
        ('wishlist', 'Список бажань'),
        ('order', 'Оформлення замовлення'),
    ]
    
    selected_pages = forms.MultipleChoiceField(
        choices=PAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Вибір сторінок",
        help_text="Виберіть сторінки. Якщо обрано 'Всі сторінки', інші вибори ігноруються",
        initial=['all']
    )
    
    class Meta:
        model = TrackingPixel
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Завантажити вибрані сторінки з бази
        if self.instance and self.instance.pk:
            pages_str = self.instance.pages or 'all'
            self.fields['selected_pages'].initial = [p.strip() for p in pages_str.split(',')]
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        selected = self.cleaned_data.get('selected_pages', [])
        
        # Якщо вибрано 'all', зберегти тільки 'all'
        if 'all' in selected:
            instance.pages = 'all'
        elif selected:
            instance.pages = ','.join(selected)
        else:
            instance.pages = 'all'  # За замовчуванням
        
        if commit:
            instance.save()
        return instance


@admin.register(TrackingPixel)
class TrackingPixelAdmin(admin.ModelAdmin):
    form = TrackingPixelAdminForm
    list_display = ['name', 'pixel_type', 'pixel_id', 'placement', 'pages_display', 'is_active', 'created_at']
    list_filter = ['pixel_type', 'placement', 'is_active', 'created_at']
    search_fields = ['name', 'pixel_id']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'pixel_type', 'pixel_id', 'is_active')
        }),
        ('Розміщення', {
            'fields': ('placement', 'selected_pages'),
            'description': 'Виберіть де і на яких сторінках показувати піксель'
        }),
        ('Код пікселя', {
            'fields': ('code_snippet',),
            'description': 'Вставте повний код включно з <script> тегами'
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def pages_display(self, obj):
        """Показати перелік сторінок у списку"""
        if obj.pages == 'all':
            return '🌐 Всі'
        pages = obj.pages.split(',')
        return ', '.join(pages[:3]) + ('...' if len(pages) > 3 else '')
    pages_display.short_description = "Сторінки"


admin.site.site_header = "Адміністрування"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Панель управління"
