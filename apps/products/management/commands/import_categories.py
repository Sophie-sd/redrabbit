"""
Команда для імпорту категорій з XML фіду постачальника
"""
import xml.etree.ElementTree as ET
import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Category


class Command(BaseCommand):
    help = 'Імпортує категорії з XML фіду постачальника'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
            help='URL XML фіду для імпорту'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Видалити всі існуючі категорії перед імпортом'
        )

    def handle(self, *args, **options):
        url = options['url']
        clear = options['clear']

        self.stdout.write(self.style.SUCCESS(f'Завантаження категорій з {url}...'))

        try:
            # Завантажуємо XML
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Парсимо XML
            root = ET.fromstring(response.content)
            
            # Видаляємо існуючі категорії якщо потрібно
            if clear:
                deleted_count = Category.objects.all().delete()[0]
                self.stdout.write(self.style.WARNING(f'Видалено {deleted_count} категорій'))
            
            # Знаходимо блок категорій
            categories_elem = root.find('.//categories')
            if categories_elem is None:
                self.stdout.write(self.style.ERROR('Не знайдено блок categories в XML'))
                return
            
            # Збираємо всі категорії спочатку
            categories_data = []
            for cat_elem in categories_elem.findall('category'):
                cat_id = cat_elem.get('id')
                parent_id = cat_elem.get('parentId')
                name = cat_elem.text.strip() if cat_elem.text else ''
                
                if not name:
                    continue
                
                categories_data.append({
                    'external_id': cat_id,
                    'parent_id': parent_id,
                    'name': name,
                })
            
            self.stdout.write(f'Знайдено {len(categories_data)} категорій для імпорту')
            
            # Створюємо словник для швидкого пошуку
            created_categories = {}
            
            # Спочатку створюємо всі головні категорії (без parent)
            for cat_data in categories_data:
                if not cat_data['parent_id']:
                    # Генеруємо унікальний slug
                    base_slug = slugify(cat_data['name'])
                    slug = base_slug
                    counter = 1
                    
                    # Перевіряємо унікальність slug (крім поточної категорії)
                    while Category.objects.filter(slug=slug).exclude(external_id=cat_data['external_id']).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    category, created = Category.objects.update_or_create(
                        external_id=cat_data['external_id'],
                        defaults={
                            'name': cat_data['name'],
                            'slug': slug,
                            'is_active': True,
                        }
                    )
                    created_categories[cat_data['external_id']] = category
                    
                    if created:
                        self.stdout.write(f'  ✓ Створено головну категорію: {category.name}')
                    else:
                        self.stdout.write(f'  ↻ Оновлено головну категорію: {category.name}')
            
            # Потім створюємо підкатегорії (кілька проходів для глибокої вкладеності)
            max_iterations = 10
            remaining = [cat for cat in categories_data if cat['parent_id']]
            
            for iteration in range(max_iterations):
                if not remaining:
                    break
                
                processed = []
                for cat_data in remaining:
                    parent_external_id = cat_data['parent_id']
                    
                    # Перевіряємо чи батьківська категорія вже створена
                    if parent_external_id in created_categories:
                        parent_category = created_categories[parent_external_id]
                        
                        # Генеруємо унікальний slug
                        base_slug = slugify(f"{parent_category.slug}-{cat_data['name']}")
                        slug = base_slug
                        counter = 1
                        
                        # Перевіряємо унікальність slug
                        while Category.objects.filter(slug=slug).exclude(external_id=cat_data['external_id']).exists():
                            slug = f"{base_slug}-{counter}"
                            counter += 1
                        
                        category, created = Category.objects.update_or_create(
                            external_id=cat_data['external_id'],
                            defaults={
                                'name': cat_data['name'],
                                'slug': slug,
                                'parent': parent_category,
                                'is_active': True,
                            }
                        )
                        created_categories[cat_data['external_id']] = category
                        
                        if created:
                            self.stdout.write(f'  ✓ Створено підкатегорію: {category.name} (батько: {parent_category.name})')
                        else:
                            self.stdout.write(f'  ↻ Оновлено підкатегорію: {category.name}')
                        
                        processed.append(cat_data)
                
                # Видаляємо оброблені
                for cat_data in processed:
                    remaining.remove(cat_data)
                
                if not processed:
                    break
            
            # Якщо залишилися необроблені
            if remaining:
                self.stdout.write(self.style.WARNING(f'Не вдалося обробити {len(remaining)} категорій (батьківські категорії не знайдені)'))
                for cat_data in remaining:
                    self.stdout.write(f'  - {cat_data["name"]} (parent_id: {cat_data["parent_id"]})')
            
            total_created = len(created_categories)
            self.stdout.write(self.style.SUCCESS(f'\n✓ Імпорт завершено! Створено/оновлено {total_created} категорій'))
            
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Помилка завантаження XML: {e}'))
        except ET.ParseError as e:
            self.stdout.write(self.style.ERROR(f'Помилка парсингу XML: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Непередбачена помилка: {e}'))

