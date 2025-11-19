#!/usr/bin/env python3
"""
Скрипт для очищення дублікатів категорій
Використовується один раз перед повним імпортом
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.development')
django.setup()

from django.db.models import Count
from apps.products.models import Category, Product


def cleanup_duplicate_categories():
    """Знаходить та видаляє дублікати категорій"""
    
    print('\n' + '='*70)
    print('🔍 ПОШУК ТА ОЧИЩЕННЯ ДУБЛІКАТІВ КАТЕГОРІЙ')
    print('='*70 + '\n')
    
    # Знаходимо дублікати за назвою
    duplicates = Category.objects.values('name').annotate(
        count=Count('id')
    ).filter(count__gt=1).order_by('-count')
    
    if not duplicates:
        print('✅ Дублікатів не знайдено!')
        return
    
    print(f'📋 Знайдено {len(duplicates)} груп дублікатів:\n')
    
    total_removed = 0
    total_merged_products = 0
    
    for dup in duplicates:
        name = dup['name']
        count = dup['count']
        
        print(f'📦 Категорія "{name}" - {count} дублікатів')
        
        # Отримуємо всі категорії з цією назвою
        cats = list(Category.objects.filter(name=name).order_by('id'))
        
        # Вибираємо головну (першу створену з найменшим ID)
        main_cat = cats[0]
        duplicates_to_remove = cats[1:]
        
        print(f'   ├─ Залишаємо: ID={main_cat.id}, slug={main_cat.slug}, '
              f'external_id={main_cat.external_id}, товарів={main_cat.products.count()}')
        
        # Переносимо товари з дублікатів в головну категорію
        for dup_cat in duplicates_to_remove:
            products_count = dup_cat.products.count()
            primary_products_count = dup_cat.primary_products.count()
            
            print(f'   ├─ Видаляємо: ID={dup_cat.id}, slug={dup_cat.slug}, '
                  f'external_id={dup_cat.external_id}, товарів={products_count}')
            
            # Переносимо товари де ця категорія в ManyToMany
            for product in dup_cat.products.all():
                if main_cat not in product.categories.all():
                    product.categories.add(main_cat)
                product.categories.remove(dup_cat)
            
            # Переносимо товари де ця категорія primary
            updated = dup_cat.primary_products.update(primary_category=main_cat)
            if updated:
                print(f'      └─ Перенесено {updated} товарів з primary_category')
                total_merged_products += updated
            
            # Переносимо дочірні категорії
            children_count = dup_cat.children.count()
            if children_count > 0:
                dup_cat.children.update(parent=main_cat)
                print(f'      └─ Перенесено {children_count} підкатегорій')
            
            # Видаляємо дублікат
            dup_cat.delete()
            total_removed += 1
        
        print()
    
    # Підсумок
    print('='*70)
    print('✅ ОЧИЩЕННЯ ЗАВЕРШЕНО!')
    print(f'📊 Видалено дублікатів: {total_removed}')
    print(f'📦 Перенесено товарів: {total_merged_products}')
    print('='*70 + '\n')
    
    # Перевіряємо чи залишилися дублікати
    remaining_dups = Category.objects.values('name').annotate(
        count=Count('id')
    ).filter(count__gt=1).count()
    
    if remaining_dups:
        print(f'⚠️  УВАГА: Залишилося {remaining_dups} груп дублікатів')
    else:
        print('✅ Всі дублікати успішно видалено!')


def check_products_without_categories():
    """Перевіряє товари без категорій"""
    
    print('\n' + '='*70)
    print('🔍 ПЕРЕВІРКА ТОВАРІВ БЕЗ КАТЕГОРІЙ')
    print('='*70 + '\n')
    
    no_primary = Product.objects.filter(primary_category__isnull=True).count()
    print(f'📦 Товарів без primary_category: {no_primary}')
    
    no_categories = Product.objects.filter(categories__isnull=True).count()
    print(f'📦 Товарів без жодної категорії: {no_categories}')
    
    inactive_cat = Product.objects.filter(
        primary_category__is_active=False
    ).count()
    print(f'📦 Товарів з неактивною primary_category: {inactive_cat}')
    
    inactive_products = Product.objects.filter(is_active=False).count()
    print(f'📦 Неактивних товарів: {inactive_products}')
    
    print('='*70 + '\n')


def show_statistics():
    """Показує загальну статистику"""
    
    print('\n' + '='*70)
    print('📊 ЗАГАЛЬНА СТАТИСТИКА')
    print('='*70 + '\n')
    
    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    parent_categories = Category.objects.filter(parent__isnull=True).count()
    
    print(f'📁 Категорій всього: {total_categories}')
    print(f'   ├─ Активних: {active_categories}')
    print(f'   └─ Головних (без батьківських): {parent_categories}')
    
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    in_stock = Product.objects.filter(stock__gt=0).count()
    
    print(f'\n📦 Товарів всього: {total_products}')
    print(f'   ├─ Активних: {active_products}')
    print(f'   └─ В наявності (stock > 0): {in_stock}')
    
    print('='*70 + '\n')


if __name__ == '__main__':
    try:
        show_statistics()
        cleanup_duplicate_categories()
        check_products_without_categories()
        show_statistics()
    except Exception as e:
        print(f'\n❌ Помилка: {e}')
        import traceback
        traceback.print_exc()

