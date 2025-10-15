"""
Management команда для створення базових категорій товарів
"""
from django.core.management.base import BaseCommand
from apps.products.models import Category


class Command(BaseCommand):
    help = 'Створює базові категорії товарів для інтим-магазину'

    def handle(self, *args, **options):
        self.stdout.write('Створення базових категорій товарів...')
        
        # Категорії для створення (інтим-магазин)
        categories_data = [
            ('Акційні товари', 'sale', 1),
            ('Для чоловіків', 'for-men', 2),
            ('Для жінок', 'for-women', 3),
            ('Для пар', 'for-couples', 4),
            ('Білизна', 'lingerie', 5),
            ('Аксесуари', 'accessories', 6),
            ('Інтимна косметика', 'intimate-cosmetics', 7),
            ('Подарункові набори', 'gift-sets', 8),
            ('Новинки', 'new-arrivals', 9),
            ('Хіти продажів', 'bestsellers', 10),
        ]
        
        created_count = 0
        updated_count = 0
        
        for name, slug, sort_order in categories_data:
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'sort_order': sort_order,
                    'is_active': True,
                    'parent': None
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Створено категорію: {name}')
                )
            else:
                # Оновлюємо існуючу категорію
                category.name = name
                category.sort_order = sort_order
                category.is_active = True
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Оновлено категорію: {name}')
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Готово! Створено: {created_count}, Оновлено: {updated_count}'
            )
        )
        
        # Перевіряємо результат
        total_categories = Category.objects.filter(is_active=True).count()
        self.stdout.write(
            self.style.SUCCESS(f'📊 Всього активних категорій: {total_categories}')
        )
