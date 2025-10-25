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
        'name', 'code', 'discount_type', 'discount_value', 
        'get_usage', 'is_active', 'start_date', 'end_date'
    ]
    list_filter = ['is_active', 'discount_type', 'start_date', 'end_date']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    readonly_fields = ['uses_count', 'created_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'code', 'is_active')
        }),
        ('Знижка', {
            'fields': (('discount_type', 'discount_value'), 'min_order_amount')
        }),
        ('Термін дії', {
            'fields': (('start_date', 'end_date'),)
        }),
        ('Обмеження', {
            'fields': (('max_uses', 'uses_count'),)
        }),
    )
    
    actions = ['activate_promotions', 'deactivate_promotions']
    
    def get_usage(self, obj):
        if obj.max_uses:
            percentage = (obj.uses_count / obj.max_uses) * 100
            return format_html(
                '<span class="badge">{}/{} ({}%)</span>',
                obj.uses_count, obj.max_uses, round(percentage)
            )
        return format_html('<span class="badge">{}</span>', obj.uses_count)
    get_usage.short_description = 'Використань'
    
    def activate_promotions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активовано {updated} акцій")
    activate_promotions.short_description = "✓ Активувати акції"
    
    def deactivate_promotions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивовано {updated} акцій")
    deactivate_promotions.short_description = "✗ Деактивувати акції"


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
