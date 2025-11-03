#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from django.core.management import call_command
from django.db import connection
from apps.products.models import Product, Category, ProductReview

print('\n' + '='*70)
print('🔧 НАЛАШТУВАННЯ PRODUCTION БД')
print('='*70 + '\n')

product_count = Product.objects.count()
category_count = Category.objects.count()

print(f'📊 Поточний стан:')
print(f'   Категорій: {category_count}')
print(f'   Товарів: {product_count}\n')

# Виправлення таблиці відгуків якщо потрібно
print('🔧 Перевірка структури таблиці відгуків...')
with connection.cursor() as cursor:
    try:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='products_productreview' 
            AND column_name='product_id'
        """)
        if not cursor.fetchone():
            print('⚠️  Поле product_id відсутнє - додаємо...')
            cursor.execute("""
                ALTER TABLE products_productreview 
                ADD COLUMN product_id BIGINT 
                REFERENCES products_product(id) ON DELETE CASCADE
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS products_pr_product_160d92_idx 
                ON products_productreview (product_id, is_approved)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS products_pr_is_appr_b55fbf_idx 
                ON products_productreview (is_approved, created_at DESC)
            """)
            print('✓ Поле product_id додано\n')
        else:
            print('✓ Структура таблиці відгуків правильна\n')
    except Exception as e:
        print(f'⚠️  Помилка при перевірці таблиці відгуків: {e}\n')

# Імпортуємо товари ТІЛЬКИ якщо БД пуста
if product_count == 0:
    print('🆕 Перший запуск - імпорт товарів з XML...\n')
    
    if category_count > 0 and product_count < 1000:
        print('⚠️  Очищення застарілих даних...\n')
        call_command('cleanup_db', full=True)
        print()
    
    print('📥 Запуск initial_import.py...\n')
    if os.path.exists('initial_import.py'):
        exec(open('initial_import.py').read())
    else:
        print('⚠️  Файл initial_import.py не знайдено')
        print('💡 Імпорт товарів потрібно виконати вручну через management команди\n')
else:
    print(f'✓ БД вже містить {product_count} товарів')
    print('✓ Пропускаємо імпорт (щоб не витрачати 20+ хвилин)\n')
    print('💡 Якщо потрібен реімпорт - видаліть всі товари вручну через admin\n')

# Створення відгуків якщо немає
review_count = ProductReview.objects.filter(is_approved=True).count()
print(f'📝 Відгуків в БД: {review_count}')
if review_count == 0 and product_count > 0:
    print('🆕 Створюємо тестові відгуки...')
    try:
        call_command('create_reviews')
        print('✓ Відгуки створено\n')
    except Exception as e:
        print(f'⚠️  Помилка при створенні відгуків: {e}\n')
else:
    print('✓ Відгуки вже існують\n')

print('\n' + '='*70)
print('✅ ГОТОВО!')
print('='*70 + '\n')

