#!/usr/bin/env python3
"""
Скрипт для виправлення production БД після невдалої міграції 0011
Запускати через Render Shell: python fix_production_db.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.db import connection
from django.core.management import call_command

print('\n' + '='*70)
print('🔧 ВИПРАВЛЕННЯ PRODUCTION БД')
print('='*70 + '\n')

with connection.cursor() as cursor:
    # Перевірка чи існує video_url
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='products_product' AND column_name='video_url'
    """)
    video_url_exists = cursor.fetchone() is not None
    
    # Перевірка чи існує products_brand
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name='products_brand'
    """)
    brand_exists = cursor.fetchone() is not None
    
    # Перевірка чи існує products_productreview
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name='products_productreview'
    """)
    review_exists = cursor.fetchone() is not None

print('📊 Стан БД:')
print(f'   video_url поле: {"✅ існує" if video_url_exists else "❌ відсутнє"}')
print(f'   Brand таблиця: {"✅ існує" if brand_exists else "❌ відсутня"}')
print(f'   ProductReview таблиця: {"✅ існує" if review_exists else "❌ відсутня"}')
print()

# Якщо video_url не існує - додаємо вручну
if not video_url_exists:
    print('🔄 Додаємо video_url поле...')
    with connection.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE products_product 
            ADD COLUMN video_url VARCHAR(200) DEFAULT '' NOT NULL
        """)
        cursor.execute("""
            ALTER TABLE products_product 
            ALTER COLUMN video_url DROP DEFAULT
        """)
    print('✅ video_url поле додано')
else:
    print('✅ video_url вже існує')

# Позначаємо міграції як виконані
print('\n🔄 Синхронізація міграцій...')

from django.db.migrations.recorder import MigrationRecorder
recorder = MigrationRecorder(connection)

# Перевірка міграції 0011
migration_0011 = recorder.migration_qs.filter(app='products', name='0011_add_video_url').exists()
if not migration_0011:
    print('   Позначаємо 0011_add_video_url як виконану...')
    recorder.record_applied('products', '0011_add_video_url')
    print('   ✅ 0011 позначена')
else:
    print('   ✅ 0011 вже позначена')

# Перевірка міграції 0012
if brand_exists and review_exists:
    migration_0012 = recorder.migration_qs.filter(app='products', name='0012_add_brand_review').exists()
    if not migration_0012:
        print('   Позначаємо 0012_add_brand_review як виконану (fake)...')
        recorder.record_applied('products', '0012_add_brand_review')
        print('   ✅ 0012 позначена (fake)')
    else:
        print('   ✅ 0012 вже позначена')

print('\n✅ Виправлення завершено!')
print('='*70)
print('🔄 Тепер перезапустіть сервер через Render Dashboard')
print('='*70 + '\n')

