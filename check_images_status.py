#!/usr/bin/env python3
"""
Скрипт для перевірки стану картинок товарів
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from apps.products.models import Product, Category
from django.db.models import Count

print('\n' + '='*70)
print('📊 СТАН КАРТИНОК ТОВАРІВ')
print('='*70)

# Загальна статистика
total_products = Product.objects.count()
with_images = Product.objects.filter(images__isnull=False).distinct().count()
without_images = Product.objects.filter(images__isnull=True).count()
active_products = Product.objects.filter(is_active=True).count()

print(f'\n🏪 ЗАГАЛЬНА СТАТИСТИКА:')
print(f'   • Всього товарів: {total_products:,}')
print(f'   • Активних товарів: {active_products:,}')
print(f'   • З картинками: {with_images:,}')
print(f'   • Без картинок: {without_images:,}')

if total_products > 0:
    progress = round(with_images/total_products*100, 1)
    print(f'   • Прогрес: {progress}%')

# Статистика по категоріям (топ-10)
print(f'\n📁 ТОП-10 КАТЕГОРІЙ БЕЗ КАРТИНОК:')
categories_without_images = Category.objects.annotate(
    products_without_images=Count('product', filter=Product.objects.filter(images__isnull=True).values('id'))
).filter(products_without_images__gt=0).order_by('-products_without_images')[:10]

if categories_without_images:
    for cat in categories_without_images:
        total_in_cat = cat.product_set.count()
        without_in_cat = cat.products_without_images
        print(f'   • {cat.name}: {without_in_cat}/{total_in_cat} товарів')
else:
    print('   ✅ Всі категорії мають товари з картинками!')

# Останні оновлення
print(f'\n🕒 ОСТАННІ ОНОВЛЕННЯ:')
recent_with_images = Product.objects.filter(
    images__isnull=False
).distinct().order_by('-updated_at')[:5]

if recent_with_images:
    for product in recent_with_images:
        images_count = product.images.count()
        print(f'   • {product.name[:50]}... ({images_count} фото) - {product.updated_at.strftime("%d.%m.%Y %H:%M")}')
else:
    print('   Немає товарів з картинками')

# Рекомендації
print(f'\n💡 РЕКОМЕНДАЦІЇ:')
if without_images > 0:
    print(f'   • Запустіть: ./download_all_images.py')
    print(f'   • Або для тестування: ./test_images_download.py')
    if without_images > 1000:
        print(f'   • Великий обсяг - буде тривати 2-4 години')
    print(f'   • Налаштуйте автооновлення: ./setup_sync_cron.sh')
else:
    print('   ✅ Всі товари мають картинки!')
    print('   • Налаштуйте автооновлення для нових товарів: ./setup_sync_cron.sh')

print('\n' + '='*70 + '\n')
