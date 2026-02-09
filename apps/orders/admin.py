from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from django.contrib import messages
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Order, OrderItem, Promotion, Newsletter
from .services.novapost import NovaPostService, NovaPostServiceError
from django.conf import settings
import logging


logger = logging.getLogger(__name__)


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
        'final_total', 'payment_method', 'is_paid', 'promo_code', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'delivery_method', 'is_paid', 'created_at']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'promo_code']
    readonly_fields = [
        'order_number', 'created_at', 'updated_at',
        'first_name', 'last_name', 'patronymic', 'phone', 'email',
        'delivery_method', 'nova_poshta_city', 'nova_poshta_city_ref',
        'nova_poshta_warehouse', 'nova_poshta_warehouse_ref',
        'ukrposhta_city', 'ukrposhta_address', 'ukrposhta_index',
        'payment_method', 'payment_date', 'payment_intent_id',
        'subtotal_retail', 'product_discount', 'promo_code', 'promo_discount', 'final_total',
        'notes', 'nova_poshta_ttn', 'get_ttn_link'
    ]
    list_editable = ['status', 'is_paid']
    date_hierarchy = 'created_at'
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Замовлення', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Клієнт', {
            'fields': ('first_name', 'last_name', 'patronymic', 'phone', 'email')
        }),
        ('Доставка', {
            'fields': ('delivery_method', 
                      ('nova_poshta_city', 'nova_poshta_city_ref'),
                      ('nova_poshta_warehouse', 'nova_poshta_warehouse_ref'),
                      'ukrposhta_city', 'ukrposhta_address', 'ukrposhta_index',
                      ('nova_poshta_ttn', 'get_ttn_link'))
        }),
        ('Ціни', {
            'fields': ('subtotal_retail', 'product_discount', 'promo_code', 'promo_discount', 'final_total')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'is_paid', 'payment_date', 'payment_intent_id')
        }),
        ('Примітки', {
            'fields': ('notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_cancelled', 'mark_as_completed', 'create_nova_poshta_ttn']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items__product')
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"Підтверджено {updated} замовлень")
    mark_as_confirmed.short_description = "Підтвердити замовлення"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"Скасовано {updated} замовлень")
    mark_as_cancelled.short_description = "✗ Скасувати замовлення"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"Завершено {updated} замовлень")
    mark_as_completed.short_description = "✓ Завершити замовлення"
    
    def get_ttn_link(self, obj):
        """Посилання на ТТН у Новій Пошті"""
        if obj.nova_poshta_ttn:
            ttn = obj.nova_poshta_ttn
            url = f"https://track.novaposhta.ua/uk?number={ttn}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, ttn)
        return "-"
    get_ttn_link.short_description = "Посилання на ТТН"
    
    def create_nova_poshta_ttn(self, request, queryset):
        """
        Action для створення ТТН через Nova Poshta API
        Перевіряє наявність всіх необхідних даних замовлення та контактів відправника
        """
        if not settings.NOVAPOST_API_KEY:
            self.message_user(
                request,
                "Помилка: NOVAPOST_API_KEY не налаштований",
                messages.ERROR
            )
            return
        
        # Фільтруємо замовлення
        valid_orders = []
        invalid_orders = []
        
        for order in queryset:
            # Перевірка умов для створення ТТН
            errors = []
            
            if order.delivery_method != 'nova_poshta':
                errors.append("Метод доставки не Nova Poshta")
            
            if not order.nova_poshta_city_ref:
                errors.append("Не вказаний REF міста")
            
            if not order.nova_poshta_warehouse_ref:
                errors.append("Не вказаний REF відділення")
            
            if not order.is_paid:
                errors.append("Замовлення не оплачено")
            
            if order.nova_poshta_ttn:
                errors.append("ТТН вже створена")
            
            if errors:
                invalid_orders.append((order.order_number, errors))
            else:
                valid_orders.append(order)
        
        # Повідомлення про невалідні замовлення
        if invalid_orders:
            for order_num, errors in invalid_orders:
                self.message_user(
                    request,
                    f"Замовлення #{order_num}: {'; '.join(errors)}",
                    messages.WARNING
                )
        
        if not valid_orders:
            if not invalid_orders:
                self.message_user(
                    request,
                    "Не вибрано замовлень для створення ТТН",
                    messages.INFO
                )
            return
        
        # Спробуємо отримати дані відправника
        try:
            np_service = NovaPostService(settings.NOVAPOST_API_KEY)
            
            # Отримуємо контрагента (правильний sender_ref)
            counterparty = np_service.get_counterparty()
            if not counterparty:
                self.message_user(
                    request,
                    "Помилка: Не знайдено контрагента (відправника). "
                    "Перевірте налаштування в кабінету Нової Пошти",
                    messages.ERROR
                )
                return
            
            # Отримуємо адреси та контакти
            sender_addresses = np_service.get_sender_addresses()
            sender_contacts = np_service.get_sender_contacts()
            
            if not sender_addresses or not sender_contacts:
                self.message_user(
                    request,
                    "Помилка: Не можна отримати дані відправника. "
                    "Перевірте налаштування в кабінету Нової Пошти",
                    messages.ERROR
                )
                return
            
            # Беремо правильні REF
            sender_ref = counterparty.get('Ref')
            sender_address = sender_addresses[0]
            sender_address_ref = sender_address.get('Ref')
            sender_city_ref = sender_address.get('CityRef')
            contact_ref = sender_contacts[0].get('Ref')
            
            if not all([sender_ref, sender_address_ref, sender_city_ref, contact_ref]):
                self.message_user(
                    request,
                    "Помилка: Неповні дані відправника. "
                    "Перевірте налаштування в кабінету Нової Пошти",
                    messages.ERROR
                )
                return
            
            # Створюємо ТТН для кожного замовлення
            successful = 0
            failed = 0
            
            for order in valid_orders:
                try:
                    # Розраховуємо вагу та вартість
                    weight = max(1000, sum(
                        item.product.weight * item.quantity 
                        for item in order.items.all()
                    )) if hasattr(order.items.first().product if order.items.exists() else None, 'weight') else 1000
                    
                    cost = str(int(order.final_total))
                    
                    result = np_service.create_shipment(
                        recipient_city_ref=order.nova_poshta_city_ref,
                        recipient_warehouse_ref=order.nova_poshta_warehouse_ref,
                        recipient_name=order.get_customer_name(),
                        recipient_phone=order.phone,
                        sender_ref=sender_ref,
                        sender_city_ref=sender_city_ref,
                        sender_address_ref=sender_address_ref,
                        sender_contact_ref=contact_ref,
                        description=f"Замовлення #{order.order_number}",
                        cost=cost,
                        weight=str(int(weight))
                    )
                    
                    if result.get('success') and result.get('data'):
                        # Отримуємо номер документа (ТТН)
                        ttn = result['data'][0].get('IntDocNumber')
                        if ttn:
                            order.nova_poshta_ttn = ttn
                            order.save(update_fields=['nova_poshta_ttn'])
                            successful += 1
                        else:
                            self.message_user(
                                request,
                                f"Замовлення #{order.order_number}: Не отримано номер ТТН",
                                messages.WARNING
                            )
                            failed += 1
                    else:
                        errors = result.get('errors', ['Невідома помилка'])
                        self.message_user(
                            request,
                            f"Замовлення #{order.order_number}: {'; '.join(errors)}",
                            messages.WARNING
                        )
                        failed += 1
                
                except NovaPostServiceError as e:
                    self.message_user(
                        request,
                        f"Замовлення #{order.order_number}: {str(e)}",
                        messages.WARNING
                    )
                    failed += 1
                except Exception as e:
                    logger.exception(f"Error creating TTN for order {order.id}: {e}")
                    self.message_user(
                        request,
                        f"Замовлення #{order.order_number}: Внутрішня помилка",
                        messages.ERROR
                    )
                    failed += 1
            
            # Фінальне повідомлення
            if successful > 0:
                self.message_user(
                    request,
                    f"✓ Успішно створено {successful} ТТН",
                    messages.SUCCESS
                )
            if failed > 0:
                self.message_user(
                    request,
                    f"✗ Помилок при створенні ТТН: {failed}",
                    messages.ERROR
                )
        
        except NovaPostServiceError as e:
            self.message_user(
                request,
                f"Помилка API Нової Пошти: {str(e)}",
                messages.ERROR
            )
        except Exception as e:
            logger.exception(f"Error in create_nova_poshta_ttn action: {e}")
            self.message_user(
                request,
                "Внутрішня помилка при створенні ТТН",
                messages.ERROR
            )
    
    create_nova_poshta_ttn.short_description = "📮 Створити ТТН для Нової Пошти"
    
    def changelist_view(self, request, extra_context=None):
        from datetime import datetime, time
        
        extra_context = extra_context or {}
        
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        
        # Загальна статистика по статусах
        pending_count = qs.filter(status='pending').count()
        in_progress_count = qs.filter(status='confirmed').count()
        completed_count = qs.filter(status='completed').count()
        
        # Статистика за сьогодні (UTC діапазон)
        today_utc = timezone.now().date()
        start_of_day = timezone.make_aware(
            datetime.combine(today_utc, time.min),
            timezone.utc
        )
        end_of_day = timezone.make_aware(
            datetime.combine(today_utc, time.max),
            timezone.utc
        )
        
        today_orders = qs.filter(created_at__gte=start_of_day, created_at__lte=end_of_day)
        
        new_today_count = today_orders.filter(status='pending').count()
        today_sum = today_orders.exclude(status='cancelled').aggregate(Sum('final_total'))['final_total__sum'] or 0
        cancelled_today_count = qs.filter(status='cancelled', updated_at__gte=start_of_day, updated_at__lte=end_of_day).count()
        
        metrics = {
            'status_stats': {
                'pending': pending_count,
                'in_progress': in_progress_count,
                'completed': completed_count,
            },
            'today_stats': {
                'date': today_utc,
                'new_orders': new_today_count,
                'sum': today_sum,
                'cancelled': cancelled_today_count,
            }
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
