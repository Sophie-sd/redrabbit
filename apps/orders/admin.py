"""
Адміністративна панель для замовлень
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Newsletter, Promotion


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_cost']
    
    def get_cost(self, obj):
        if obj.id:
            return f"{obj.get_cost():.2f} грн"
        return "0.00 грн"
    
    get_cost.short_description = "Вартість"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Адміністрування замовлень"""
    
    list_display = [
        'order_number', 'get_customer_name', 'status', 
        'total', 'payment_method', 'is_paid', 'created_at'
    ]
    list_filter = [
        'status', 'payment_method', 'delivery_method', 
        'is_paid', 'created_at'
    ]
    search_fields = [
        'order_number', 'first_name', 'last_name', 
        'email', 'phone'
    ]
    readonly_fields = [
        'order_number', 'created_at', 'updated_at',
        'get_total_cost', 'get_customer_info'
    ]
    list_editable = ['status', 'is_paid']
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Клієнт', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'get_customer_info')
        }),
        ('Доставка', {
            'fields': (
                'delivery_method', 'delivery_city', 
                'delivery_address', 'delivery_cost'
            )
        }),
        ('Оплата', {
            'fields': (
                'payment_method', 'is_paid', 'payment_date',
                'subtotal', 'discount', 'total', 'get_total_cost'
            )
        }),
        ('Примітки', {
            'fields': ('notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']
    
    def get_customer_info(self, obj):
        """Інформація про клієнта"""
        if obj.user:
            wholesale_status = "Опт" if obj.user.is_wholesale else "Роздріб"
            return format_html(
                '<strong>{}</strong><br>Email: {}<br>Телефон: {}<br>Статус: {}',
                obj.get_customer_name(),
                obj.email,
                obj.phone,
                wholesale_status
            )
        return format_html(
            '<strong>{}</strong><br>Email: {}<br>Телефон: {}',
            obj.get_customer_name(),
            obj.email,
            obj.phone
        )
    
    get_customer_info.short_description = "Інформація про клієнта"
    
    def get_total_cost(self, obj):
        """Загальна вартість з доставкою"""
        return f"{obj.get_total_cost():.2f} грн"
    
    get_total_cost.short_description = "Загальна вартість"
    
    def mark_as_confirmed(self, request, queryset):
        """Підтвердити замовлення"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"Підтверджено {updated} замовлень")
    
    mark_as_confirmed.short_description = "Підтвердити замовлення"
    
    def mark_as_shipped(self, request, queryset):
        """Відправити замовлення"""
        updated = queryset.update(status='shipped')
        self.message_user(request, f"Відправлено {updated} замовлень")
    
    mark_as_shipped.short_description = "Відправити замовлення"
    
    def mark_as_delivered(self, request, queryset):
        """Доставлено замовлення"""
        updated = queryset.update(status='delivered')
        self.message_user(request, f"Доставлено {updated} замовлень")
    
    mark_as_delivered.short_description = "Доставлено замовлення"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Адміністрування розсилки"""
    
    list_display = ['email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email']
    list_editable = ['is_active']
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        """Активувати підписки"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активовано {updated} підписок")
    
    activate_subscriptions.short_description = "Активувати підписки"
    
    def deactivate_subscriptions(self, request, queryset):
        """Деактивувати підписки"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивовано {updated} підписок")
    
    deactivate_subscriptions.short_description = "Деактивувати підписки"


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Адміністрування акцій"""
    
    list_display = [
        'name', 'code', 'discount_type', 'discount_value',
        'is_active', 'start_date', 'end_date', 'uses_count'
    ]
    list_filter = [
        'discount_type', 'is_active', 'start_date', 'end_date'
    ]
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'code')
        }),
        ('Знижка', {
            'fields': (
                'discount_type', 'discount_value', 
                'min_order_amount'
            )
        }),
        ('Обмеження', {
            'fields': (
                'max_uses', 'uses_count',
                'start_date', 'end_date', 'is_active'
            )
        }),
    )
    
    readonly_fields = ['uses_count']
    
    actions = ['activate_promotions', 'deactivate_promotions']
    
    def activate_promotions(self, request, queryset):
        """Активувати акції"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активовано {updated} акцій")
    
    activate_promotions.short_description = "Активувати акції"
    
    def deactivate_promotions(self, request, queryset):
        """Деактивувати акції"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивовано {updated} акцій")
    
    deactivate_promotions.short_description = "Деактивувати акції"
