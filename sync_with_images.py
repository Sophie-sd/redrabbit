#!/usr/bin/env python3
"""
Скрипт для повної синхронізації товарів з картинками
Використовується для періодичного оновлення (cron)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.core.management import call_command

print('\n' + '='*70)
print('🔄 СИНХРОНІЗАЦІЯ З ПОСТАЧАЛЬНИКОМ (З КАРТИНКАМИ)')
print('='*70 + '\n')

try:
    call_command(
        'sync_products',
        url='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
        batch_size=50,
        verbosity=1
    )
    print('\n✅ Синхронізація завершена успішно!')
    
except Exception as e:
    print(f'\n❌ Помилка синхронізації: {e}')
    exit(1)

print('='*70 + '\n')
