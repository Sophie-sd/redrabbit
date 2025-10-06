"""
Адміністративна панель для core додатку - банери
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """Адмін панель для банерів"""
    
    list_display = [
        'title', 
        'desktop_preview', 
        'mobile_preview', 
        'is_active', 
        'has_link',
        'order', 
        'created_at'
    ]
    
    list_filter = [
        'is_active', 
        'created_at'
    ]
    
    search_fields = [
        'title', 
        'alt_text', 
        'link_url'
    ]
    
    list_editable = [
        'is_active', 
        'order'
    ]
    
    readonly_fields = [
        'created_at', 
        'updated_at',
        'desktop_preview_large',
        'mobile_preview_large'
    ]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'alt_text', 'is_active', 'order')
        }),
        ('Зображення', {
            'fields': (
                ('desktop_image', 'desktop_preview_large'),
                ('mobile_image', 'mobile_preview_large'),
            ),
            'description': mark_safe("""
                <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h4 style="color: #0066cc; margin-top: 0;">📐 Розміри зображень:</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>Десктоп:</strong> 1200×400 пікселів (співвідношення 3:1)</li>
                        <li><strong>Мобільний:</strong> 375×280 пікселів (співвідношення 1.34:1)</li>
                    </ul>
                    <p style="color: #666; margin: 0; font-style: italic;">
                        Підтримувані формати: JPG, PNG, WebP
                    </p>
                </div>
            """)
        }),
        ('Посилання', {
            'fields': ('link_url',),
            'description': 'URL на який переходити при натисканні на банер (необов\'язково)'
        }),
        ('Системні дані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def desktop_preview(self, obj):
        """Превью десктопного зображення в списку"""
        if obj.desktop_image:
            return format_html(
                '<img src="{}" alt="{}" style="width: 60px; height: 20px; object-fit: cover; border-radius: 4px;" />',
                obj.desktop_image.url,
                obj.alt_text
            )
        return "Немає"
    desktop_preview.short_description = "Превью десктоп"
    
    def mobile_preview(self, obj):
        """Превью мобільного зображення в списку"""
        if obj.mobile_image:
            return format_html(
                '<img src="{}" alt="{}" style="width: 40px; height: 21px; object-fit: cover; border-radius: 4px;" />',
                obj.mobile_image.url,
                obj.alt_text
            )
        return "Немає"
    mobile_preview.short_description = "Превью мобільний"
    
    def desktop_preview_large(self, obj):
        """Велике превью десктопного зображення"""
        if obj.desktop_image:
            return format_html(
                '''
                <div style="margin: 10px 0;">
                    <img src="{}" alt="{}" style="max-width: 300px; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">Десктоп версія</p>
                </div>
                ''',
                obj.desktop_image.url,
                obj.alt_text
            )
        return "Зображення не завантажено"
    desktop_preview_large.short_description = "Превью десктоп"
    
    def mobile_preview_large(self, obj):
        """Велике превью мобільного зображення"""
        if obj.mobile_image:
            return format_html(
                '''
                <div style="margin: 10px 0;">
                    <img src="{}" alt="{}" style="max-width: 187px; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">Мобільна версія</p>
                </div>
                ''',
                obj.mobile_image.url,
                obj.alt_text
            )
        return "Зображення не завантажено"
    mobile_preview_large.short_description = "Превью мобільний"
    
    def has_link(self, obj):
        """Чи є посилання"""
        if obj.link_url:
            return format_html(
                '<span style="color: green;">✓ Є</span>'
            )
        return format_html(
            '<span style="color: #999;">Немає</span>'
        )
    has_link.short_description = "Посилання"
    
    def get_queryset(self, request):
        """Оптимізація запитів"""
        return super().get_queryset(request).select_related()
        
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)


# Додаткові налаштування адмін панелі
admin.site.site_header = "Beauty Shop - Управління банерами"
admin.site.site_title = "Beauty Shop Admin"
admin.site.index_title = "Панель управління"
