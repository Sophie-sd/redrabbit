#!/usr/bin/env python3
"""
Швидкий скрипт для додавання URL зображень (без завантаження файлів)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.core.management import call_command

print('\n' + '='*70)
print('🖼️  ШВИДКЕ ДОДАВАННЯ URL ЗОБРАЖЕНЬ')
print('='*70 + '\n')

try:
    call_command('bulk_add_image_urls')
    print('\n✅ Додавання URL завершене!')
    
except Exception as e:
    print(f'\n❌ Помилка: {e}')
    exit(1)

print('='*70 + '\n')

