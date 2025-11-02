import xml.etree.ElementTree as ET
import requests
import html
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.products.models import Category, Product, ProductAttribute
from apps.products.utils import download_product_images


class Command(BaseCommand):
    help = 'Імпортує товари з XML фіду постачальника'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
            help='URL XML фіду для імпорту'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Максимальна кількість товарів для імпорту (для тестування)'
        )
        parser.add_argument(
            '--update-only',
            action='store_true',
            help='Тільки оновлювати існуючі товари, не створювати нові'
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Не завантажувати зображення товарів'
        )

    def handle(self, *args, **options):
        url = options['url']
        limit = options['limit']
        update_only = options['update_only']
        skip_images = options['skip_images']

        self.stdout.write(self.style.SUCCESS(f'Завантаження товарів з {url}...'))

        try:
            # Завантажуємо XML
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Парсимо XML
            root = ET.fromstring(response.content)
            
            # Перевіряємо наявність категорій в базі
            categories_count = Category.objects.count()
            if categories_count == 0:
                self.stdout.write(self.style.ERROR('Немає категорій в базі! Спочатку виконайте: python manage.py import_categories'))
                return
            
            self.stdout.write(f'Знайдено {categories_count} категорій в базі')
            
            # Створюємо індекс категорій по external_id
            categories_index = {
                cat.external_id: cat 
                for cat in Category.objects.all() 
                if cat.external_id
            }
            
            # Знаходимо блок товарів
            offers_elem = root.find('.//offers')
            if offers_elem is None:
                self.stdout.write(self.style.ERROR('Не знайдено блок offers в XML'))
                return
            
            offers = offers_elem.findall('offer')
            total_offers = len(offers)
            
            if limit:
                offers = offers[:limit]
                self.stdout.write(f'Обмеження: імпорт лише {limit} товарів з {total_offers}')
            else:
                self.stdout.write(f'Знайдено {total_offers} товарів для імпорту')
            
            # Лічильники
            created_count = 0
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            for idx, offer in enumerate(offers, 1):
                try:
                    # Отримуємо дані товару
                    offer_id = offer.get('id')
                    available = offer.get('available', 'true') == 'true'
                    
                    # Базові дані
                    category_id = self._get_text(offer, 'categoryId')
                    price = self._get_text(offer, 'price')
                    vendor_code = self._get_text(offer, 'vendorCode')
                    vendor = self._get_text(offer, 'vendor')
                    name = self._get_text(offer, 'name')
                    description = self._get_text(offer, 'description')
                    
                    # Пропускаємо якщо немає обов'язкових полів
                    if not name or not price or not category_id:
                        self.stdout.write(f'  ⚠ Пропущено товар {offer_id}: відсутні обов\'язкові поля')
                        skipped_count += 1
                        continue
                    
                    # Знаходимо категорію
                    category = categories_index.get(category_id)
                    if not category:
                        self.stdout.write(f'  ⚠ Пропущено товар {name}: категорія {category_id} не знайдена')
                        skipped_count += 1
                        continue
                    
                    # Конвертуємо ціну
                    try:
                        retail_price = Decimal(price)
                    except (ValueError, TypeError):
                        self.stdout.write(f'  ⚠ Пропущено товар {name}: некоректна ціна {price}')
                        skipped_count += 1
                        continue
                    
                    # Обробляємо HTML в описі
                    if description:
                        description = html.unescape(description)
                    
                    # Перевіряємо чи товар існує
                    existing_product = None
                    if vendor_code:
                        existing_product = Product.objects.filter(external_id=vendor_code).first()
                    
                    # Якщо режим тільки оновлення і товару немає - пропускаємо
                    if update_only and not existing_product:
                        skipped_count += 1
                        continue
                    
                    # Дані для створення/оновлення
                    product_data = {
                        'name': name[:200],
                        'description': description or '',
                        'retail_price': retail_price,
                        'vendor_name': vendor[:200] if vendor else '',
                        'is_active': available,
                        'stock': 5 if available else 0,
                        'is_sale': False,
                        'sale_price': None,
                    }
                    
                    # Створюємо або оновлюємо товар
                    if existing_product:
                        # Оновлюємо існуючий
                        for key, value in product_data.items():
                            setattr(existing_product, key, value)
                        
                        # Оновлюємо категорії
                        if not existing_product.primary_category:
                            existing_product.primary_category = category
                        
                        existing_product.save()
                        
                        # Додаємо в categories якщо немає
                        if category not in existing_product.categories.all():
                            existing_product.categories.add(category)
                        
                        product = existing_product
                        updated_count += 1
                        action = '↻'
                    else:
                        # Створюємо новий
                        product = Product.objects.create(
                            external_id=vendor_code or offer_id,
                            primary_category=category,
                            **product_data
                        )
                        # Додаємо в ManyToMany після створення
                        product.categories.add(category)
                        
                        created_count += 1
                        action = '✓'
                    
                    if not skip_images:
                        pictures = offer.findall('picture')
                        if pictures:
                            picture_urls = [p.text for p in pictures if p.text]
                            success, errors = download_product_images(product, picture_urls)
                            if errors > 0:
                                self.stdout.write(f'    Помилки завантаження: {errors}')
                    
                    # Характеристики
                    params = offer.findall('param')
                    if params:
                        # Видаляємо старі атрибути
                        product.attributes.all().delete()
                        
                        # Додаємо нові
                        for param_idx, param in enumerate(params):
                            param_name = param.get('name')
                            param_value = param.text
                            
                            if param_name and param_value:
                                ProductAttribute.objects.create(
                                    product=product,
                                    name=param_name[:100],
                                    value=param_value[:200],
                                    sort_order=param_idx,
                                )
                    
                    # Виводимо прогрес кожні 50 товарів
                    if idx % 50 == 0:
                        self.stdout.write(f'  {action} Оброблено {idx}/{len(offers)} товарів...')
                    
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'  ✗ Помилка обробки товару {offer_id}: {e}'))
            
            # Підсумок
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('✓ Імпорт завершено!'))
            self.stdout.write(f'  Створено нових: {created_count}')
            self.stdout.write(f'  Оновлено: {updated_count}')
            self.stdout.write(f'  Пропущено: {skipped_count}')
            if error_count > 0:
                self.stdout.write(self.style.WARNING(f'  Помилок: {error_count}'))
            self.stdout.write(self.style.SUCCESS('='*60))
            
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Помилка завантаження XML: {e}'))
        except ET.ParseError as e:
            self.stdout.write(self.style.ERROR(f'Помилка парсингу XML: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Непередбачена помилка: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def _get_text(self, element, tag):
        """Безпечно отримує текст з XML елемента"""
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return ''

