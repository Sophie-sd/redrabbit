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
        'username', 
        'email', 
        'phone',
        'first_name', 
        'last_name', 
        'is_wholesale',
        'email_verified',
        'is_active',
        'date_joined'
    ]
    
    list_filter = [
        'is_wholesale',
        'email_verified',
        'is_active',
        'is_staff',
        'date_joined'
    ]
    
    search_fields = [
        'username',
        'email',
        'phone',
        'first_name',
        'last_name'
    ]
    
    readonly_fields = [
        'monthly_turnover',
        'last_turnover_update',
        'email_verified',
        'created_at',
        'date_joined',
        'last_login'
    ]
    
    fieldsets = UserAdmin.fieldsets + (
        ('Персональні дані', {
            'fields': ('phone', 'date_of_birth')
        }),
        ('Email верифікація', {
            'fields': ('email_verified', 'email_verification_token'),
            'classes': ('collapse',)
        }),
        ('Оптовий статус', {
            'fields': ('is_wholesale', 'monthly_turnover', 'last_turnover_update')
        }),
        ('Дати', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Основна інформація', {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'phone',
                'first_name',
                'last_name',
                'date_of_birth',
                'password1',
                'password2',
            ),
        }),
        ('Статус', {
            'fields': ('is_wholesale', 'is_active'),
        }),
    )
    
    actions = ['make_wholesale', 'remove_wholesale', 'verify_email_action', 'activate_users_action', 'update_wholesale_status']
    
    def make_wholesale(self, request, queryset):
        """Надати оптовий статус"""
        updated = queryset.update(is_wholesale=True)
        self.message_user(request, f'{updated} користувачів отримали оптовий статус.')
    make_wholesale.short_description = 'Надати оптовий статус'
    
    def remove_wholesale(self, request, queryset):
        """Забрати оптовий статус"""
        updated = queryset.update(is_wholesale=False)
        self.message_user(request, f'{updated} користувачів втратили оптовий статус.')
    remove_wholesale.short_description = 'Забрати оптовий статус'
    
    def verify_email_action(self, request, queryset):
        """Підтвердити email вручну"""
        updated = queryset.update(email_verified=True, is_active=True, email_verification_token='')
        self.message_user(request, f'{updated} email адрес підтверджено.')
    verify_email_action.short_description = 'Підтвердити email'
    
    def activate_users_action(self, request, queryset):
        """Активувати користувачів (без підтвердження email)"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} користувачів активовано.')
    activate_users_action.short_description = 'Активувати користувачів'
    
    def update_wholesale_status(self, request, queryset):
        """Оновити статус оптових клієнтів"""
        count = 0
        for user in queryset:
            user.update_wholesale_status()
            count += 1
        self.message_user(request, f"Оновлено статус для {count} користувачів")
    update_wholesale_status.short_description = "Оновити статус оптових клієнтів"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Адміністрування профілів користувачів"""
    
    list_display = ['user', 'company_name', 'tax_number']
    search_fields = ['user__username', 'company_name', 'tax_number']
    list_filter = ['user__is_wholesale']
