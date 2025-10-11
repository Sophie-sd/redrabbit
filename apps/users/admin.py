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
        'is_wholesale',
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
            'fields': ('is_wholesale',),
            'description': 'Всі зареєстровані користувачі автоматично отримують оптовий статус'
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
            'fields': ('is_active',),
        }),
    )
    
    actions = ['verify_email_action', 'activate_users_action']
    
    def verify_email_action(self, request, queryset):
        """Підтвердити email вручну"""
        updated = queryset.update(email_verified=True, is_active=True, is_wholesale=True, email_verification_token='')
        self.message_user(request, f'{updated} email адрес підтверджено та надано оптовий статус.')
    verify_email_action.short_description = 'Підтвердити email та активувати'
    
    def activate_users_action(self, request, queryset):
        """Активувати користувачів"""
        updated = queryset.update(is_active=True, is_wholesale=True)
        self.message_user(request, f'{updated} користувачів активовано з оптовим статусом.')
    activate_users_action.short_description = 'Активувати користувачів'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Адміністрування профілів користувачів"""
    
    list_display = ['user', 'company_name', 'tax_number']
    search_fields = ['user__username', 'company_name', 'tax_number']
    list_filter = ['user__is_wholesale']
