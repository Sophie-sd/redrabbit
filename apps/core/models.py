"""
Моделі для core додатку - банери головної сторінки
"""
from django.db import models
from django.core.validators import FileExtensionValidator


class Banner(models.Model):
    """Модель для банерів на головній сторінці"""
    
    title = models.CharField(
        max_length=200,
        verbose_name="Назва банера",
        help_text="Назва для ідентифікації в адмін панелі"
    )
    
    # Зображення для різних пристроїв
    desktop_image = models.ImageField(
        upload_to='banners/desktop/',
        verbose_name="Зображення для десктопу",
        help_text="Розмір: 1200×400 пікселів (співвідношення 3:1)",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    
    mobile_image = models.ImageField(
        upload_to='banners/mobile/',
        verbose_name="Зображення для мобільного",
        help_text="Розмір: 375×280 пікселів (співвідношення 1.34:1)",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    
    # Посилання
    link_url = models.URLField(
        verbose_name="Посилання",
        help_text="URL на який переходити при натисканні на банер",
        blank=True,
        null=True
    )
    
    # Додаткові поля
    alt_text = models.CharField(
        max_length=255,
        verbose_name="Alt текст",
        help_text="Текст для accessibility та SEO",
        default="Банер RedRabbit"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активний",
        help_text="Показувати банер на сайті"
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортування",
        help_text="Менше число = вище в списку"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Створено"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Оновлено"
    )
    
    class Meta:
        verbose_name = "Банер"
        verbose_name_plural = "Банери"
        ordering = ['order', '-created_at']
        
    def __str__(self):
        return f"{self.title} ({'Активний' if self.is_active else 'Неактивний'})"
        
    def save(self, *args, **kwargs):
        # Автоматично генеруємо alt_text якщо не заповнений
        if not self.alt_text:
            self.alt_text = f"Банер: {self.title}"
        super().save(*args, **kwargs)


class TrackingPixel(models.Model):
    """Модель для керування tracking pixels (Google Analytics, Facebook Pixel, GTM)"""
    
    PIXEL_TYPES = [
        ('facebook', 'Facebook Pixel'),
        ('google_analytics', 'Google Analytics'),
        ('google_tag_manager', 'Google Tag Manager'),
        ('custom', 'Custom Pixel'),
    ]
    
    PLACEMENT_CHOICES = [
        ('head', 'Head Section'),
        ('body_start', 'Body Start'),
        ('body_end', 'Body End'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name="Назва пікселя",
        help_text="Описова назва для ідентифікації"
    )
    
    pixel_type = models.CharField(
        max_length=50,
        choices=PIXEL_TYPES,
        verbose_name="Тип пікселя"
    )
    
    pixel_id = models.CharField(
        max_length=100,
        verbose_name="ID пікселя",
        help_text="Наприклад: G-XXXXXXXXXX для GA, або 1234567890 для FB Pixel"
    )
    
    code_snippet = models.TextField(
        verbose_name="Код пікселя",
        help_text="Повний код включно з <script> тегами"
    )
    
    placement = models.CharField(
        max_length=20,
        choices=PLACEMENT_CHOICES,
        default='head',
        verbose_name="Розташування",
        help_text="Де вставити код на сторінці"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активний",
        help_text="Чи працює піксель зараз"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Створено"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Оновлено"
    )
    
    class Meta:
        verbose_name = "Tracking Pixel"
        verbose_name_plural = "📊 Tracking Pixels"
        ordering = ['-created_at']
        unique_together = [['pixel_type', 'pixel_id']]
    
    def __str__(self):
        return f"{self.name} ({self.get_pixel_type_display()})"
