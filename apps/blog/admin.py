from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from ckeditor.widgets import CKEditorWidget
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Адміністрування статей"""
    
    list_display = [
        'title', 'get_image_preview', 'is_published', 
        'created_at', 'get_excerpt_preview'
    ]
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'excerpt', 'image')
        }),
        ('Контент', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Публікація', {
            'fields': ('is_published',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    # Кастомні віджети
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }
    
    actions = ['publish_articles', 'unpublish_articles', 'duplicate_articles']
    
    def get_image_preview(self, obj):
        """Попередній перегляд зображення"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "📷 Немає"
    
    get_image_preview.short_description = "Зображення"
    
    def get_excerpt_preview(self, obj):
        """Попередній перегляд опису"""
        if obj.excerpt:
            return obj.excerpt[:50] + "..." if len(obj.excerpt) > 50 else obj.excerpt
        return "Немає опису"
    
    get_excerpt_preview.short_description = "Короткий опис"
    
    def publish_articles(self, request, queryset):
        """Опублікувати статті"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Опубліковано {updated} статей")
    
    publish_articles.short_description = "Опублікувати вибрані статті"
    
    def unpublish_articles(self, request, queryset):
        """Сховати статті"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Сховано {updated} статей")
    
    unpublish_articles.short_description = "Сховати вибрані статті"
    
    def duplicate_articles(self, request, queryset):
        """Дублювати статті"""
        duplicated = 0
        for article in queryset:
            # Створюємо копію
            article.pk = None
            article.title = f"{article.title} (копія)"
            article.slug = f"{article.slug}-copy"
            article.is_published = False
            article.save()
            duplicated += 1
        
        self.message_user(request, f"Продубльовано {duplicated} статей")
    
    duplicate_articles.short_description = "Дублювати вибрані статті"
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)