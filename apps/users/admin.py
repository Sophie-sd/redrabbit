"""
Адміністративна панель користувачів
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Адміністрування користувачів (адміністраторів)"""
    
    list_display = ['username', 'first_name', 'email', 'phone', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'date_joined', 'last_login']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Контактні дані', {
            'fields': ('phone',),
        }),
        ('Системні дати', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Основна інформація', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Права доступу', {
            'fields': ('is_staff', 'is_active'),
        }),
    )
