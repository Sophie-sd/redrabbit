#!/usr/bin/env python3
"""
Скрипт для початкового імпорту товарів на Render.com
Запускається один раз при першому deploy
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.core.management import call_command
from apps.products.models import Product

print('\n' + '='*70)
print('🚀 ПОЧАТКОВИЙ ІМПОРТ ТОВАРІВ')
print('='*70 + '\n')

# Перевіряємо чи вже є товари
product_count = Product.objects.count()

if product_count > 100:
    print(f'✓ Товари вже імпортовані: {product_count} шт.')
    print('ℹ️  Пропускаємо імпорт. Для оновлення використовуйте update_prices.')
else:
    print(f'📊 Поточна кількість товарів: {product_count}')
    print('🔄 Запускаємо повний імпорт товарів...\n')
    
    try:
        call_command(
            'import_products',
            url='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
            skip_images=True,
            verbosity=1
        )
        
        new_count = Product.objects.count()
        print(f'\n✅ Імпорт завершено! Всього товарів: {new_count}')
        
    except Exception as e:
        print(f'\n❌ Помилка імпорту: {e}')
        print('⚠️  Build продовжиться без товарів.')

print('='*70 + '\n')

