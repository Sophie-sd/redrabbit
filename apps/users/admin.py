from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'email', 'phone', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Контакти', {
            'fields': ('phone',),
        }),
    )
