from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .models import Order, OrderItem, Promotion, Newsletter


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    fields = ['product', 'quantity', 'price']
    readonly_fields = ['product', 'quantity', 'price']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'get_customer_name', 'status', 
        'total', 'payment_method', 'is_paid', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'delivery_method', 'is_paid', 'created_at']
    search_fields = ['order_number', 'first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    list_editable = ['status', 'is_paid']
    date_hierarchy = 'created_at'
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Замовлення', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Клієнт', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Доставка', {
            'fields': ('delivery_method', 'delivery_city', 'delivery_address', 'delivery_cost')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'is_paid', 'payment_date', 'subtotal', 'discount', 'total')
        }),
        ('Примітки', {
            'fields': ('notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('items__product')
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"Підтверджено {updated} замовлень")
    mark_as_confirmed.short_description = "Підтвердити замовлення"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f"Відправлено {updated} замовлень")
    mark_as_shipped.short_description = "Відправити замовлення"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f"Доставлено {updated} замовлень")
    mark_as_delivered.short_description = "Доставлено замовлення"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        
        metrics = {
            'total': qs.count(),
            'total_revenue': qs.aggregate(Sum('total'))['total__sum'] or 0,
            'average_order': qs.aggregate(Avg('total'))['total__avg'] or 0,
            'paid_orders': qs.filter(is_paid=True).count(),
        }
        
        response.context_data['summary'] = metrics
        
        return response


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'get_discount_display', 'apply_to',
        'get_usage', 'get_status', 'is_active', 'start_date', 'end_date'
    ]
    list_filter = ['is_active', 'discount_type', 'apply_to', 'start_date']
    search_fields = ['name', 'code']
    list_editable = []
    readonly_fields = ['uses_count', 'created_at']
    filter_horizontal = ['categories']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'code', 'is_active'),
            'description': '<strong>Назва</strong> - для вашої зручності в адмінці. <strong>Промокод</strong> - що вводить покупець у кошику.'
        }),
        ('Умови знижки', {
            'fields': (
                ('discount_type', 'discount_value'),
                'min_order_amount',
            ),
            'description': 'Встановіть тип та розмір знижки'
        }),
        ('Застосування промокоду', {
            'fields': (
                'apply_to',
                'categories',
            ),
            'description': 'Виберіть до яких товарів застосовується промокод'
        }),
        ('Термін дії', {
            'fields': (('start_date', 'end_date'),),
            'description': 'Промокод буде активним тільки в цей період'
        }),
        ('Обмеження використання', {
            'fields': (('max_uses', 'uses_count'),),
        }),
    )
    
    actions = ['activate_promotions', 'deactivate_promotions', 'duplicate_promo']
    
    def get_discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return format_html('<strong>{}%</strong>', obj.discount_value)
        return format_html('<strong>{} ₴</strong>', obj.discount_value)
    get_discount_display.short_description = 'Знижка'
    
    def get_usage(self, obj):
        if obj.max_uses:
            percentage = (obj.uses_count / obj.max_uses) * 100
            color = '#4CAF50' if percentage < 80 else '#ff9800' if percentage < 100 else '#f44336'
            return format_html(
                '<span style="color: {}; font-weight: 600;">{}/{}</span>',
                color, obj.uses_count, obj.max_uses
            )
        return format_html('<span style="color: #2196F3;">{}</span>', obj.uses_count)
    get_usage.short_description = 'Використань'
    
    def get_status(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: #4CAF50; font-weight: 600;">✓ Активний</span>')
        elif not obj.is_active:
            return format_html('<span style="color: #999;">✗ Вимкнено</span>')
        else:
            return format_html('<span style="color: #ff9800;">⏰ Неактивний</span>')
    get_status.short_description = 'Статус'
    
    def activate_promotions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активовано {updated} промокодів")
    activate_promotions.short_description = "✓ Активувати"
    
    def deactivate_promotions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивовано {updated} промокодів")
    deactivate_promotions.short_description = "✗ Деактивувати"
    
    def duplicate_promo(self, request, queryset):
        for promo in queryset:
            promo.pk = None
            promo.code = f"{promo.code}_copy"
            promo.uses_count = 0
            promo.save()
        self.message_user(request, f"Створено {queryset.count()} копій промокодів")
    duplicate_promo.short_description = "📋 Дублювати"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email']
    list_editable = ['is_active']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    actions = ['export_emails']
    
    def export_emails(self, request, queryset):
        emails = queryset.filter(is_active=True).values_list('email', flat=True)
        emails_list = ', '.join(emails)
        self.message_user(request, f"Активні email ({len(emails)}): {emails_list}")
    export_emails.short_description = "📧 Експортувати email"
