#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.core.management import call_command
from apps.products.models import Product, Category

print('\n' + '='*70)
print('🔧 НАЛАШТУВАННЯ PRODUCTION БД')
print('='*70 + '\n')

product_count = Product.objects.count()
category_count = Category.objects.count()

print(f'📊 Поточний стан:')
print(f'   Категорій: {category_count}')
print(f'   Товарів: {product_count}\n')

if category_count > 0 and product_count < 1000:
    print('⚠️  Очищення застарілих даних...\n')
    call_command('cleanup_db', full=True)
    print()

print('📥 Запуск initial_import.py...\n')
exec(open('initial_import.py').read())

print('\n' + '='*70)
print('✅ ГОТОВО!')
print('='*70 + '\n')

