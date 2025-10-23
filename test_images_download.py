#!/usr/bin/env python3
"""
Тестовий скриптт для перевірки завантаження картинок
Завантажує картинки тільки для 10 товарів для тестування
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.core.management import call_command

print('\n' + '='*70)
print('🧪 ТЕСТОВЕ ЗАВАНТАЖЕННЯ КАРТИНОК (10 товарів)')
print('='*70 + '\n')

try:
    # Тестуємо на 10 товарах для швидкої перевірки
    call_command(
        'bulk_download_images',
        url='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
        batch_size=10,
        delay=0.2,
        max_retries=2,
        verbosity=2
    )
    
    print('\n✅ Тестове завантаження завершене!')
    print('\n📋 Для повного завантаження запустіть:')
    print('   python3 download_all_images.py')
    
except Exception as e:
    print(f'\n❌ Помилка тестування: {e}')
    exit(1)

print('='*70 + '\n')
