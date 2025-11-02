"""
Моделі товарів та категорій
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
import time


class Category(models.Model):
    """Категорії товарів з підтримкою ієрархії"""
    
    CATEGORY_TYPES = [
        ('general', 'Загальна'),
        ('women', 'Для жінок'),
        ('men', 'Для чоловіків'),
        ('couple', 'Для пар'),
    ]
    
    name = models.CharField('Назва', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    external_id = models.CharField(
        'Зовнішній ID', 
        max_length=50, 
        blank=True, 
        null=True, 
        unique=True,
        help_text='ID категорії в системі постачальника'
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='Батьківська категорія'
    )
    image = models.ImageField('Зображення', upload_to='categories/', blank=True)
    icon = models.CharField('Іконка', max_length=50, blank=True, help_text='Emoji або CSS клас')
    category_type = models.CharField('Тип категорії', max_length=20, choices=CATEGORY_TYPES, default='general')
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
        if not self.slug:
            return '#'
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
    """Товари"""
    
    name = models.CharField('Назва', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='products', verbose_name='Категорії', blank=True)
    primary_category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='primary_products', 
        verbose_name='Основна категорія',
        help_text='Категорія для URL та основного відображення'
    )
    description = models.TextField('Опис', blank=True)
    
    # Ціна
    retail_price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    
    # Акція (з файлів постачальника)
    is_sale = models.BooleanField('Акційний товар', default=False)
    sale_price = models.DecimalField(
        'Акційна ціна', 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    sale_name = models.CharField(
        'Назва акції',
        max_length=200,
        blank=True,
        default='',
        help_text='Назва акції для відображення на стікері'
    )
    sale_start_date = models.DateTimeField(
        'Дата початку акції',
        null=True,
        blank=True,
        help_text='Залиште порожнім для необмеженої акції'
    )
    sale_end_date = models.DateTimeField(
        'Дата закінчення акції',
        null=True,
        blank=True,
        help_text='Акція автоматично завершиться після цієї дати'
    )
    
    # Бейджі (встановлюються в адмінці)
    is_top = models.BooleanField('Хіт', default=False)
    is_new = models.BooleanField('Новинка', default=False)
    
    # Додаткові поля
    sku = models.CharField('Артикул', max_length=50, unique=True, blank=True)
    external_id = models.CharField(
        'Зовнішній ID', 
        max_length=50, 
        blank=True, 
        null=True,
        db_index=True,
        help_text='Артикул постачальника (vendorCode)'
    )
    vendor_name = models.CharField(
        'Постачальник', 
        max_length=200, 
        blank=True,
        help_text='Назва бренду/постачальника з фіду'
    )
    stock = models.PositiveIntegerField('Кількість на складі', default=0)
    is_active = models.BooleanField('Активний', default=True)
    is_featured = models.BooleanField('Рекомендований', default=False)
    sort_order = models.PositiveIntegerField('Порядок сортування', default=0)
    
    # Дати
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)
    
    # Зв'язки
    tags = models.ManyToManyField(
        'ProductTag', 
        verbose_name='Теги', 
        blank=True,
        help_text='Теги для фільтрації товарів'
    )
    
    # Відео
    video_url = models.URLField(
        'Відео URL',
        blank=True,
        help_text='Посилання на YouTube або Vimeo відео товару'
    )
    
    # SEO поля
    meta_title = models.CharField('SEO заголовок', max_length=200, blank=True)
    meta_description = models.TextField('SEO опис', max_length=300, blank=True)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['primary_category', 'is_active']),
            models.Index(fields=['is_active', 'is_sale', 'is_new', 'is_top']),
            models.Index(fields=['sku']),
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
            # Індекси для пошуку
            models.Index(fields=['name']),
            models.Index(fields=['is_active', 'name']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        generate_sku = not self.sku
        
        if generate_sku:
            self.sku = f"TEMP{int(time.time() * 1000000)}"
        
        super().save(*args, **kwargs)
        
        if generate_sku:
            self.sku = f"BS{self.id:05d}"
            Product.objects.filter(pk=self.pk).update(sku=self.sku)
    
    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})
    
    @property
    def main_image(self):
        """Повертає головне зображення товару"""
        return self.images.filter(is_main=True).first() or self.images.first()
    
    def is_sale_active(self):
        """Перевіряє чи активна акція (враховуючи терміни)"""
        if not self.is_sale or not self.sale_price:
            return False
        
        from django.utils import timezone
        now = timezone.now()
        
        if self.sale_start_date and now < self.sale_start_date:
            return False
        
        if self.sale_end_date and now > self.sale_end_date:
            return False
        
        return True
    
    def get_current_price(self):
        """Повертає актуальну ціну (акційну якщо є, інакше звичайну)"""
        if self.is_sale_active():
            return self.sale_price
        return self.retail_price
    
    def get_discount_percentage(self):
        """Розраховує відсоток знижки"""
        if self.is_sale_active() and self.retail_price > 0:
            discount = ((self.retail_price - self.sale_price) / self.retail_price) * 100
            return round(discount)
        return 0
    
    def get_stickers(self):
        """Повертає список активних стікерів (бейджів)"""
        stickers = []
        if self.is_top:
            stickers.append({'type': 'top', 'text': 'ТОП ПРОДАЖ', 'class': 'badge-top'})
        if self.is_new:
            stickers.append({'type': 'new', 'text': 'Новинка', 'class': 'badge-new'})
        if self.is_sale_active():
            discount = self.get_discount_percentage()
            if discount > 0:
                stickers.append({'type': 'sale', 'text': f'-{discount}%', 'class': 'badge-sale'})
            else:
                stickers.append({'type': 'sale', 'text': 'Акція', 'class': 'badge-sale'})
        if self.video_url:
            stickers.append({'type': 'video', 'text': 'ВІДЕО', 'class': 'badge-video'})
        return stickers
    
    def get_similar_products(self, limit=4):
        """Повертає схожі товари з тієї ж основної категорії"""
        if not self.primary_category:
            return Product.objects.none()
        
        return Product.objects.filter(
            primary_category=self.primary_category,
            is_active=True
        ).exclude(id=self.id).order_by('?')[:limit]
    
    def is_in_stock(self):
        """Перевіряє чи є товар в наявності"""
        return self.stock > 0
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Зображення товарів"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('Зображення', upload_to='products/', blank=True, null=True)
    image_url = models.URLField('URL зображення', max_length=500, blank=True)
    alt_text = models.CharField('Alt текст', max_length=200, blank=True)
    is_main = models.BooleanField('Головне зображення', default=False)
    sort_order = models.PositiveIntegerField('Порядок', default=0)
    
    class Meta:
        verbose_name = 'Зображення товару'
        verbose_name_plural = 'Зображення товарів'
        ordering = ['sort_order']
    
    def get_image_url(self):
        """Повертає URL зображення (завантажене або зовнішнє)"""
        if self.image:
            return self.image.url
        return self.image_url
    
    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            try:
                from io import BytesIO
                from django.core.files.uploadedfile import InMemoryUploadedFile
                
                img = Image.open(self.image)
                
                if img.height > 800 or img.width > 800:
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                    
                    output = BytesIO()
                    img.save(output, format='JPEG', optimize=True, quality=85)
                    output.seek(0)
                    
                    self.image = InMemoryUploadedFile(
                        output,
                        'ImageField',
                        f"{self.image.name.split('.')[0]}.jpg",
                        'image/jpeg',
                        output.getbuffer().nbytes,
                        None
                    )
            except Exception:
                pass
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Зображення для {self.product.name}"


class ProductTag(models.Model):
    """Теги товарів для фільтрації"""
    
    name = models.CharField('Назва тегу', max_length=50, unique=True)
    slug = models.SlugField('URL', max_length=50, unique=True, blank=True)
    is_active = models.BooleanField('Активний', default=True)
    
    class Meta:
        verbose_name = 'Тег товару'
        verbose_name_plural = 'Теги товарів'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


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


class ProductReview(models.Model):
    """Відгуки користувачів про товари"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    author_name = models.CharField('Ім\'я автора', max_length=100, default='Аноним')
    rating = models.PositiveSmallIntegerField(
        'Рейтинг',
        default=5,
        help_text='Оцінка від 1 до 5'
    )
    text = models.TextField('Текст відгуку')
    category_badge = models.CharField(
        'Бейдж категорії',
        max_length=50,
        blank=True,
        help_text='Наприклад: "Піхва", "Вакуумні стимулятори"'
    )
    is_approved = models.BooleanField('Схвалено', default=False)
    created_at = models.DateTimeField('Дата створення', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Відгук про товар'
        verbose_name_plural = 'Відгуки про товари'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_approved', '-created_at']),
            models.Index(fields=['product', 'is_approved']),
        ]
    
    def __str__(self):
        return f"Відгук від {self.author_name} на {self.product.name}"


class Brand(models.Model):
    """Бренди товарів"""
    
    name = models.CharField('Назва бренду', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=100, unique=True, blank=True)
    logo = models.ImageField('Логотип', upload_to='brands/', blank=True)
    description = models.TextField('Опис', blank=True)
    is_active = models.BooleanField('Активний', default=True)
    sort_order = models.PositiveIntegerField('Порядок сортування', default=0)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренди'
        ordering = ['sort_order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
