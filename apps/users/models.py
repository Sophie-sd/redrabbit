"""
Моделі користувачів з підтримкою оптових цін
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from decimal import Decimal
import secrets


class CustomUser(AbstractUser):
    """Розширена модель користувача"""
    
    phone_validator = RegexValidator(
        regex=r'^\+380\d{9}$',
        message='Невірний формат телефону. Використовуйте формат +380XXXXXXXXX'
    )
    
    phone = models.CharField(
        'Телефон', 
        max_length=20, 
        unique=True,
        validators=[phone_validator],
        help_text='Формат: +380XXXXXXXXX'
    )
    date_of_birth = models.DateField('Дата народження', null=True, blank=True)
    
    # Email верифікація
    email_verified = models.BooleanField('Email підтверджено', default=False)
    email_verification_token = models.CharField('Токен верифікації', max_length=100, blank=True)
    
    is_wholesale = models.BooleanField('Оптовий клієнт', default=False)
    monthly_turnover = models.DecimalField(
        'Місячний оборот', 
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    last_turnover_update = models.DateTimeField(
        'Останнє оновлення обороту', 
        default=timezone.now
    )
    created_at = models.DateTimeField('Дата реєстрації', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'
    
    def generate_email_verification_token(self):
        """Генерує токен для верифікації email"""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.save(update_fields=['email_verification_token'])
        return self.email_verification_token
    
    def verify_email(self, token):
        """Верифікує email якщо токен збігається"""
        if self.email_verification_token and self.email_verification_token == token:
            self.email_verified = True
            self.is_active = True
            self.email_verification_token = ''
            self.save(update_fields=['email_verified', 'is_active', 'email_verification_token'])
            return True
        return False
    
    def update_wholesale_status(self):
        """
        Оновлює статус оптового клієнта на основі місячного обороту
        Автоматично надає статус при обороті 5000+ грн за місяць
        """
        from apps.orders.models import Order
        from datetime import datetime, timedelta
        
        # Рахуємо оборот за останній місяць
        last_month = timezone.now() - timedelta(days=30)
        monthly_orders = Order.objects.filter(
            user=self,
            created_at__gte=last_month,
            status__in=['completed', 'delivered']
        )
        
        self.monthly_turnover = sum([order.get_total_cost() for order in monthly_orders])
        
        # Автоматично надаємо оптовий статус при обороті 5000+ грн
        if self.monthly_turnover >= Decimal('5000.00'):
            self.is_wholesale = True
        
        self.last_turnover_update = timezone.now()
        self.save()
    
    def get_price_for_product(self, product):
        """
        Повертає ціну товару залежно від статусу користувача
        """
        if self.is_wholesale and product.wholesale_price:
            return product.wholesale_price
        return product.retail_price
    
    def __str__(self):
        return f"{self.username} ({'Опт' if self.is_wholesale else 'Роздріб'})"


class UserProfile(models.Model):
    """Додаткова інформація про користувача"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField('Назва компанії', max_length=200, blank=True)
    tax_number = models.CharField('Податковий номер', max_length=50, blank=True)
    address = models.TextField('Адреса', blank=True)
    notes = models.TextField('Примітки', blank=True)
    
    class Meta:
        verbose_name = 'Профіль користувача'
        verbose_name_plural = 'Профілі користувачів'
    
    def __str__(self):
        return f"Профіль {self.user.username}"
