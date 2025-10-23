#!/usr/bin/env python3
"""
Скрипт для масового завантаження картинок для всіх товарів
Використовується одноразово для початкового завантаження
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.core.management import call_command

print('\n' + '='*70)
print('🖼️  МАСОВЕ ЗАВАНТАЖЕННЯ КАРТИНОК')
print('='*70 + '\n')

try:
    call_command(
        'bulk_download_images',
        url='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
        batch_size=100,
        delay=0.1,
        max_retries=3,
        verbosity=1
    )
    print('\n✅ Завантаження картинок завершене!')
    
except Exception as e:
    print(f'\n❌ Помилка завантаження: {e}')
    exit(1)

print('='*70 + '\n')
