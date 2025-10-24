from django.contrib import admin
from django.utils.html import format_html
from .models import Banner


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


admin.site.site_header = "Адміністрування"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Панель управління"
