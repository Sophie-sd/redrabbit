"""
Адміністративна панель для користувачів
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Адміністрування користувачів"""
    
    inlines = [UserProfileInline]
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'is_wholesale', 'monthly_turnover', 'phone', 'is_active'
    ]
    list_filter = ['is_wholesale', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {
            'fields': ('phone', 'is_wholesale', 'monthly_turnover', 'last_turnover_update')
        }),
    )
    
    readonly_fields = ['monthly_turnover', 'last_turnover_update']
    
    actions = ['update_wholesale_status']
    
    def update_wholesale_status(self, request, queryset):
        """Оновити статус оптових клієнтів"""
        for user in queryset:
            user.update_wholesale_status()
        self.message_user(request, f"Оновлено статус для {queryset.count()} користувачів")
    
    update_wholesale_status.short_description = "Оновити статус оптових клієнтів"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Адміністрування профілів користувачів"""
    
    list_display = ['user', 'company_name', 'tax_number']
    search_fields = ['user__username', 'company_name', 'tax_number']
    list_filter = ['user__is_wholesale']
