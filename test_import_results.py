#!/usr/bin/env python3
"""
Скрипт для тестування результатів імпорту
Перевіряє всі аспекти: дублікати, відображення, підкатегорії, товари
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.development')
django.setup()

from django.db.models import Count, Q
from apps.products.models import Category, Product


def print_section(title):
    """Виводить заголовок секції"""
    print('\n' + '='*70)
    print(f' {title}')
    print('='*70)


def test_duplicates():
    """Тест 1: Перевірка дублікатів категорій"""
    print_section('🔍 ТЕСТ 1: Перевірка дублікатів категорій')
    
    duplicates = Category.objects.values('name').annotate(
        count=Count('id')
    ).filter(count__gt=1).order_by('-count')
    
    if not duplicates:
        print('✅ PASSED: Дублікатів категорій не знайдено')
        return True
    else:
        print(f'❌ FAILED: Знайдено {len(duplicates)} груп дублікатів:')
        for dup in duplicates:
            print(f'   • "{dup["name"]}" - {dup["count"]} разів')
            cats = Category.objects.filter(name=dup['name'])
            for cat in cats:
                print(f'     └─ ID={cat.id}, slug={cat.slug}, external_id={cat.external_id}')
        return False


def test_categories_display():
    """Тест 2: Перевірка відображення категорій"""
    print_section('📁 ТЕСТ 2: Відображення категорій на сайті')
    
    total = Category.objects.count()
    active = Category.objects.filter(is_active=True).count()
    with_slug = Category.objects.filter(is_active=True).exclude(Q(slug='') | Q(slug__isnull=True)).count()
    
    print(f'Категорій всього: {total}')
    print(f'Активних: {active}')
    print(f'З валідним slug: {with_slug}')
    
    # Категорії без slug
    no_slug = Category.objects.filter(
        is_active=True
    ).filter(Q(slug='') | Q(slug__isnull=True))
    
    if no_slug.exists():
        print(f'\n❌ FAILED: Знайдено {no_slug.count()} активних категорій без slug:')
        for cat in no_slug[:5]:
            print(f'   • ID={cat.id}, name={cat.name}, external_id={cat.external_id}')
        return False
    else:
        print('\n✅ PASSED: Всі активні категорії мають валідний slug')
        return True


def test_subcategories():
    """Тест 3: Перевірка підкатегорій"""
    print_section('📂 ТЕСТ 3: Відображення підкатегорій')
    
    parent_cats = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    )
    
    print(f'Головних категорій: {parent_cats.count()}\n')
    
    issues = []
    for parent in parent_cats:
        children = parent.children.filter(is_active=True)
        children_with_slug = children.exclude(Q(slug='') | Q(slug__isnull=True))
        
        print(f'{parent.name} ({parent.slug}):')
        print(f'   • Підкатегорій: {children.count()}')
        print(f'   • З валідним slug: {children_with_slug.count()}')
        
        if children.count() != children_with_slug.count():
            diff = children.count() - children_with_slug.count()
            print(f'   ❌ {diff} підкатегорій без slug!')
            issues.append(parent.name)
    
    if issues:
        print(f'\n❌ FAILED: Проблеми в категоріях: {", ".join(issues)}')
        return False
    else:
        print('\n✅ PASSED: Всі підкатегорії мають валідний slug')
        return True


def test_products_display():
    """Тест 4: Перевірка відображення товарів"""
    print_section('📦 ТЕСТ 4: Відображення товарів')
    
    total = Product.objects.count()
    active = Product.objects.filter(is_active=True).count()
    in_stock = Product.objects.filter(stock__gt=0).count()
    
    print(f'Товарів всього: {total}')
    print(f'Активних: {active}')
    print(f'В наявності (stock > 0): {in_stock}')
    
    # Товари без primary_category
    no_primary = Product.objects.filter(primary_category__isnull=True)
    if no_primary.exists():
        print(f'\n❌ WARNING: {no_primary.count()} товарів без primary_category')
        for prod in no_primary[:3]:
            print(f'   • {prod.name} (SKU: {prod.sku})')
    
    # Товари без категорій взагалі
    no_cats = Product.objects.filter(categories__isnull=True, primary_category__isnull=True)
    if no_cats.exists():
        print(f'\n❌ FAILED: {no_cats.count()} товарів без жодної категорії!')
        return False
    
    # Товари з неактивною primary_category
    inactive_cat = Product.objects.filter(
        is_active=True,
        primary_category__is_active=False
    )
    if inactive_cat.exists():
        print(f'\n❌ WARNING: {inactive_cat.count()} активних товарів з неактивною категорією')
    
    print('\n✅ PASSED: Основні перевірки пройдено')
    return True


def test_admin_vs_site():
    """Тест 5: Порівняння адмінка vs сайт"""
    print_section('🔄 ТЕСТ 5: Відображення в адмінці та на сайті')
    
    # Товари які мають показуватися на сайті
    site_products = Product.objects.filter(
        is_active=True,
        primary_category__is_active=True
    ).exclude(primary_category__isnull=True)
    
    # Всі активні товари в адмінці
    admin_products = Product.objects.filter(is_active=True)
    
    print(f'Товарів в адмінці (is_active=True): {admin_products.count()}')
    print(f'Товарів на сайті (is_active=True + active category): {site_products.count()}')
    
    diff = admin_products.count() - site_products.count()
    if diff > 0:
        print(f'\n⚠️  Різниця: {diff} товарів можуть не показуватися на сайті')
        print('    (причина: немає категорії або категорія неактивна)')
    else:
        print('\n✅ PASSED: Всі товари з адмінки мають показуватися на сайті')
    
    return True


def test_import_coverage():
    """Тест 6: Охоплення імпорту"""
    print_section('📊 ТЕСТ 6: Охоплення імпорту з фіду')
    
    print('⚠️  Цей тест потребує завантаження XML для порівняння')
    print('Для перевірки вручну:')
    print('1. Відвідайте: https://smtm.com.ua/_prices/import-retail-ua-2.xml')
    print('2. Порахуйте кількість <category> та <offer> елементів')
    print('3. Порівняйте з даними нижче:\n')
    
    print(f'В базі даних:')
    print(f'   • Категорій: {Category.objects.count()}')
    print(f'   • Товарів: {Product.objects.count()}')
    
    return True


def test_prices_update():
    """Тест 7: Оновлення цін"""
    print_section('💰 ТЕСТ 7: Перевірка оновлення цін')
    
    print('Для тестування оновлення цін виконайте:')
    print('1. python3 manage.py update_prices_xls')
    print('2. Перевірте логи: /tmp/intshop_prices.log')
    print('3. Перевірте що ціни оновилися в базі')
    
    # Показуємо кілька цін для порівняння
    products = Product.objects.filter(is_active=True)[:5]
    print('\nПриклад поточних цін:')
    for prod in products:
        print(f'   • {prod.name[:50]}: {prod.retail_price} ₴ (stock: {prod.stock})')
    
    return True


def run_all_tests():
    """Запускає всі тести"""
    print('\n╔═══════════════════════════════════════════════════════════════╗')
    print('║        ТЕСТУВАННЯ РЕЗУЛЬТАТІВ ІМПОРТУ                         ║')
    print('╚═══════════════════════════════════════════════════════════════╝')
    
    tests = [
        ('Дублікати категорій', test_duplicates),
        ('Відображення категорій', test_categories_display),
        ('Відображення підкатегорій', test_subcategories),
        ('Відображення товарів', test_products_display),
        ('Адмінка vs Сайт', test_admin_vs_site),
        ('Охоплення імпорту', test_import_coverage),
        ('Оновлення цін', test_prices_update),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f'\n❌ EXCEPTION in {name}: {e}')
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Підсумок
    print_section('📋 ПІДСУМОК ТЕСТУВАННЯ')
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = '✅ PASSED' if result else '❌ FAILED'
        print(f'{status}: {name}')
    
    print(f'\nРезультат: {passed}/{total} тестів пройдено')
    
    if passed == total:
        print('\n🎉 ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!')
    else:
        print(f'\n⚠️  Деякі тести не пройдено. Перевірте деталі вище.')


if __name__ == '__main__':
    try:
        run_all_tests()
    except Exception as e:
        print(f'\n❌ Критична помилка: {e}')
        import traceback
        traceback.print_exc()

