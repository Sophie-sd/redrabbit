#!/usr/bin/env python3
"""
Скрипт для оновлення цін та наявності товарів
Можна запускати періодично через Render Cron Jobs
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.core.management import call_command

print('\n' + '='*70)
print('🔄 ОНОВЛЕННЯ ЦІН ТА НАЯВНОСТІ')
print('='*70 + '\n')

try:
    call_command(
        'import_products',
        url='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
        skip_images=True,
        update_only=True,
        verbosity=1
    )
    print('\n✅ Оновлення завершено успішно!')
    
except Exception as e:
    print(f'\n❌ Помилка оновлення: {e}')
    exit(1)

print('='*70 + '\n')

