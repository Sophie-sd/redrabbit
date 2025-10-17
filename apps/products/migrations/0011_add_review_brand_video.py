# Generated manually for redrabbit rebrand
from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_cleanup_models'),
    ]

    operations = [
        # Додати video_url в Product
        migrations.AddField(
            model_name='product',
            name='video_url',
            field=models.URLField(blank=True, help_text='Посилання на YouTube або Vimeo відео товару', verbose_name='Відео URL'),
        ),
        
        # Створити модель ProductReview
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(default='Аноним', max_length=100, verbose_name="Ім'я автора")),
                ('rating', models.PositiveSmallIntegerField(default=5, help_text='Оцінка від 1 до 5', verbose_name='Рейтинг')),
                ('text', models.TextField(verbose_name='Текст відгуку')),
                ('category_badge', models.CharField(blank=True, help_text='Наприклад: "Піхва", "Вакуумні стимулятори"', max_length=50, verbose_name='Бейдж категорії')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Схвалено')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='products.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Відгук про товар',
                'verbose_name_plural': 'Відгуки про товари',
                'ordering': ['-created_at'],
            },
        ),
        
        # Створити модель Brand
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Назва бренду')),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True, verbose_name='URL')),
                ('logo', models.ImageField(blank=True, upload_to='brands/', verbose_name='Логотип')),
                ('description', models.TextField(blank=True, verbose_name='Опис')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активний')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Порядок сортування')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
            ],
            options={
                'verbose_name': 'Бренд',
                'verbose_name_plural': 'Бренди',
                'ordering': ['sort_order', 'name'],
            },
        ),
        
        # Індекси для ProductReview
        migrations.AddIndex(
            model_name='productreview',
            index=models.Index(fields=['is_approved', '-created_at'], name='products_pr_is_appr_b55fbf_idx'),
        ),
        migrations.AddIndex(
            model_name='productreview',
            index=models.Index(fields=['product', 'is_approved'], name='products_pr_product_160d92_idx'),
        ),
    ]

