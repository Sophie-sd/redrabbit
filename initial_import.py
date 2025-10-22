#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.core.management import call_command
from apps.products.models import Product, Category

print('\n' + '='*70)
print('🚀 ПОЧАТКОВИЙ ІМПОРТ КАТЕГОРІЙ ТА ТОВАРІВ')
print('='*70 + '\n')

category_count = Category.objects.count()

if category_count < 10:
    print(f'📁 Імпорт категорій...')
    try:
        call_command(
            'import_categories',
            url='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
            verbosity=1
        )
        new_cat_count = Category.objects.count()
        print(f'✅ Категорії: {new_cat_count}\n')
    except Exception as e:
        print(f'⚠️  Помилка: {e}\n')
else:
    print(f'✓ Категорії: {category_count}\n')

product_count = Product.objects.count()

if product_count > 1000:
    print(f'✓ Товари: {product_count}')
    print('ℹ️  Пропускаємо імпорт\n')
else:
    print(f'📊 Товарів: {product_count}')
    print('🔄 Імпорт товарів (без зображень)...\n')
    
    try:
        call_command(
            'import_products',
            url='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
            skip_images=True,
            verbosity=1
        )
        
        new_count = Product.objects.count()
        print(f'\n✅ Товарів: {new_count}')
        print('ℹ️  Запустіть: python manage.py download_images')
        
    except Exception as e:
        print(f'\n❌ Помилка: {e}')

print('='*70 + '\n')

