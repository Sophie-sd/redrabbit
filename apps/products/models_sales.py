"""
Модель для управління акційними пропозиціями
"""
from django.db import models
from django.db.models import Q
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Sale(models.Model):
    """Акційна пропозиція"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Відсоток від ціни'),
        ('fixed', 'Фіксована знижка'),
    ]
    
    name = models.CharField('Назва акції', max_length=200)
    discount_type = models.CharField('Тип знижки', max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField('Розмір знижки', max_digits=10, decimal_places=2)
    
    categories = models.ManyToManyField(
        'Category',
        verbose_name='Категорії',
        blank=True,
        help_text='Оберіть категорії для застосування знижки'
    )
    products = models.ManyToManyField(
        'Product',
        verbose_name='Товари',
        blank=True,
        help_text='Оберіть конкретні товари для застосування знижки'
    )
    
    start_date = models.DateTimeField('Дата початку')
    end_date = models.DateTimeField('Дата закінчення')
    
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Акційна пропозиція'
        verbose_name_plural = 'Акційні пропозиції'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'start_date', 'end_date']),
        ]
    
    def clean(self):
        if self.discount_type == 'percentage' and self.discount_value is not None:
            if self.discount_value > 100:
                raise ValidationError({
                    'discount_value': 'Відсоток знижки не може перевищувати 100%'
                })
        if self.discount_value is not None and self.discount_value <= 0:
            raise ValidationError({
                'discount_value': 'Розмір знижки повинен бути більше 0'
            })
    
    def is_active_now(self):
        """Перевіряє чи активна акція зараз"""
        if not self.is_active:
            return False
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    def get_affected_products(self):
        """Повертає всі товари, на які діє акція"""
        from .models import Product
        products = set(self.products.all())
        
        for category in self.categories.all():
            category_products = Product.objects.filter(
                Q(primary_category=category) | Q(categories=category),
                is_active=True,
                stock__gt=0
            ).distinct()
            products.update(category_products)
            
            for child_category in category.get_all_children():
                child_products = Product.objects.filter(
                    Q(primary_category=child_category) | Q(categories=child_category),
                    is_active=True,
                    stock__gt=0
                ).distinct()
                products.update(child_products)
        
        return list(products)
    
    def calculate_sale_price(self, original_price):
        """Розраховує акційну ціну"""
        if self.discount_type == 'percentage':
            discount_amount = original_price * (self.discount_value / 100)
            sale_price = original_price - discount_amount
        else:
            sale_price = original_price - self.discount_value
        
        return max(sale_price, Decimal('0.01'))
    
    def apply_to_products(self):
        """Застосовує акцію до товарів"""
        products = self.get_affected_products()
        for product in products:
            sale_price = self.calculate_sale_price(product.retail_price)
            product.is_sale = True
            product.sale_price = sale_price
            product.sale_name = self.name
            product.sale_start_date = self.start_date
            product.sale_end_date = self.end_date
            product.save(update_fields=['is_sale', 'sale_price', 'sale_name', 'sale_start_date', 'sale_end_date'])
    
    def remove_from_products(self):
        """Знімає акцію з товарів, перевіряючи чи не належать іншій активній акції"""
        products = self.get_affected_products()
        for product in products:
            other_sale = self._find_other_active_sale(product)
            if other_sale:
                other_sale._apply_to_single_product(product)
            else:
                product.is_sale = False
                product.sale_price = None
                product.sale_name = ''
                product.sale_start_date = None
                product.sale_end_date = None
                product.save(update_fields=['is_sale', 'sale_price', 'sale_name', 'sale_start_date', 'sale_end_date'])
    
    def _apply_to_single_product(self, product):
        """Застосовує акцію до одного товару"""
        sale_price = self.calculate_sale_price(product.retail_price)
        product.is_sale = True
        product.sale_price = sale_price
        product.sale_name = self.name
        product.sale_start_date = self.start_date
        product.sale_end_date = self.end_date
        product.save(update_fields=['is_sale', 'sale_price', 'sale_name', 'sale_start_date', 'sale_end_date'])
    
    def _find_other_active_sale(self, product):
        """Знаходить іншу активну акцію для товару (якщо є)"""
        now = timezone.now()
        other_sales = Sale.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
        ).exclude(pk=self.pk)
        
        for sale in other_sales:
            affected = sale.get_affected_products()
            if product in affected:
                return sale
        return None
    
    def __str__(self):
        return self.name


@receiver(pre_delete, sender=Sale)
def sale_pre_delete(sender, instance, **kwargs):
    """Знімає акцію з товарів перед видаленням Sale"""
    try:
        instance.remove_from_products()
    except Exception as e:
        logger.error(f"Error removing sale '{instance.name}' from products: {e}")


@receiver(m2m_changed, sender=Sale.categories.through)
@receiver(m2m_changed, sender=Sale.products.through)
def sale_m2m_changed(sender, instance, action, pk_set, **kwargs):
    """Застосовує або знімає акцію при зміні категорій/товарів"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        if action in ['post_remove', 'post_clear'] and instance.is_active:
            _clean_removed_products(sender, instance, action, pk_set)
        if instance.is_active:
            instance.apply_to_products()
        else:
            instance.remove_from_products()


def _clean_removed_products(sender, instance, action, pk_set):
    """Знімає акцію з товарів/категорій, що були видалені зі Sale"""
    from .models import Product
    
    if action == 'post_clear':
        return
    
    if not pk_set:
        return
    
    if sender == Sale.products.through:
        removed_products = Product.objects.filter(pk__in=pk_set)
    else:
        removed_products = Product.objects.filter(
            Q(primary_category__in=pk_set) | Q(categories__in=pk_set),
            is_active=True,
        ).distinct()
    
    for product in removed_products:
        if product.sale_name == instance.name:
            other_sale = instance._find_other_active_sale(product)
            if other_sale:
                other_sale._apply_to_single_product(product)
            else:
                product.is_sale = False
                product.sale_price = None
                product.sale_name = ''
                product.sale_start_date = None
                product.sale_end_date = None
                product.save(update_fields=['is_sale', 'sale_price', 'sale_name', 'sale_start_date', 'sale_end_date'])

