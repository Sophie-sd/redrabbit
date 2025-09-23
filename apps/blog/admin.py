from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Адміністрування статей"""
    
    list_display = ['title', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'image')
        }),
        ('Публікація', {
            'fields': ('is_published',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
