"""
Моделі товарів та категорій з підтримкою оптових цін
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal
from PIL import Image
import os


class Category(models.Model):
    """Категорії товарів з підтримкою ієрархії"""
    
    name = models.CharField('Назва', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='Батьківська категорія'
    )
    image = models.ImageField('Зображення', upload_to='categories/', blank=True)
    description = models.TextField('Опис', blank=True)
    is_active = models.BooleanField('Активна', default=True)
    sort_order = models.PositiveIntegerField('Порядок сортування', default=0)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    
    # SEO поля
    meta_title = models.CharField('SEO заголовок', max_length=200, blank=True)
    meta_description = models.TextField('SEO опис', max_length=300, blank=True)
    
    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['sort_order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category', kwargs={'slug': self.slug})
    
    def get_all_children(self):
        """Повертає всі дочірні категорії рекурсивно"""
        children = []
        for child in self.children.filter(is_active=True):
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name


class Product(models.Model):
    """Товари з підтримкою роздрібних та оптових цін"""
    
    name = models.CharField('Назва', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категорія')
    description = models.TextField('Опис', blank=True)
    
    # Ціни
    retail_price = models.DecimalField('Роздрібна ціна', max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(
        'Оптова ціна', 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Ціна для оптових клієнтів'
    )
    
    # Знижки
    is_sale = models.BooleanField('Акційний товар', default=False)
    sale_price = models.DecimalField(
        'Акційна ціна', 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Кількісні знижки
    min_quantity_discount = models.PositiveIntegerField(
        'Мінімальна кількість для знижки', 
        default=1,
        help_text='Мінімальна кількість для отримання знижки'
    )
    quantity_discount_price = models.DecimalField(
        'Ціна при великій кількості', 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Додаткові поля
    sku = models.CharField('Артикул', max_length=50, unique=True, blank=True)
    stock = models.PositiveIntegerField('Кількість на складі', default=0)
    is_active = models.BooleanField('Активний', default=True)
    is_featured = models.BooleanField('Рекомендований', default=False)
    
    # Дати
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)
    
    # SEO поля
    meta_title = models.CharField('SEO заголовок', max_length=200, blank=True)
    meta_description = models.TextField('SEO опис', max_length=300, blank=True)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"BS{self.id or '000'}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})
    
    def get_price_for_user(self, user=None, quantity=1):
        """
        Повертає ціну для конкретного користувача з урахуванням:
        - Оптового статусу
        - Кількісних знижок
        - Акційних цін
        """
        # Базова ціна
        if user and user.is_authenticated and user.is_wholesale and self.wholesale_price:
            base_price = self.wholesale_price
        else:
            base_price = self.retail_price
        
        # Акційна ціна
        if self.is_sale and self.sale_price:
            base_price = min(base_price, self.sale_price)
        
        # Кількісна знижка
        if quantity >= self.min_quantity_discount and self.quantity_discount_price:
            base_price = min(base_price, self.quantity_discount_price)
        
        return base_price
    
    def get_discount_percentage(self):
        """Розраховує відсоток знижки"""
        if self.is_sale and self.sale_price:
            discount = ((self.retail_price - self.sale_price) / self.retail_price) * 100
            return round(discount)
        return 0
    
    def is_in_stock(self):
        """Перевіряє чи є товар в наявності"""
        return self.stock > 0
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Зображення товарів"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('Зображення', upload_to='products/')
    alt_text = models.CharField('Alt текст', max_length=200, blank=True)
    is_main = models.BooleanField('Головне зображення', default=False)
    sort_order = models.PositiveIntegerField('Порядок', default=0)
    
    class Meta:
        verbose_name = 'Зображення товару'
        verbose_name_plural = 'Зображення товарів'
        ordering = ['sort_order']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Оптимізуємо зображення
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                img.save(self.image.path, optimize=True, quality=85)
    
    def __str__(self):
        return f"Зображення для {self.product.name}"


class ProductAttribute(models.Model):
    """Характеристики товарів"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField('Назва характеристики', max_length=100)
    value = models.CharField('Значення', max_length=200)
    sort_order = models.PositiveIntegerField('Порядок', default=0)
    
    class Meta:
        verbose_name = 'Характеристика товару'
        verbose_name_plural = 'Характеристики товарів'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.name}: {self.value}"
