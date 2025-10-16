"""
Команда для швидкого оновлення цін та наявності з CSV фіду
"""
import csv
import requests
from io import StringIO
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.products.models import Product


class Command(BaseCommand):
    help = 'Оновлює ціни та наявність товарів з CSV фіду'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://smtm.com.ua/_prices/price-retail.csv',
            help='URL CSV фіду для оновлення цін'
        )

    def handle(self, *args, **options):
        url = options['url']

        self.stdout.write(self.style.SUCCESS(f'Завантаження цін з {url}...'))

        try:
            # Завантажуємо CSV
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Парсимо CSV (windows-1251 кодування)
            try:
                content = response.content.decode('windows-1251')
            except UnicodeDecodeError:
                content = response.content.decode('utf-8')
            
            csv_file = StringIO(content)
            reader = csv.reader(csv_file, delimiter='|')
            
            # Пропускаємо заголовок
            next(reader, None)
            
            # Лічильники
            updated_count = 0
            not_found_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    if len(row) < 4:
                        continue
                    
                    vendor_code = row[0].strip()
                    # name = row[1].strip()  # не використовуємо
                    price = row[2].strip()
                    stock = row[3].strip()
                    
                    if not vendor_code or not price:
                        continue
                    
                    # Знаходимо товар по external_id
                    try:
                        product = Product.objects.get(external_id=vendor_code)
                    except Product.DoesNotExist:
                        not_found_count += 1
                        continue
                    
                    # Оновлюємо ціну
                    try:
                        new_price = Decimal(price)
                        product.retail_price = new_price
                    except (ValueError, TypeError):
                        error_count += 1
                        continue
                    
                    # Оновлюємо наявність
                    try:
                        stock_qty = int(stock) if stock.isdigit() else 0
                        product.stock = stock_qty
                        product.is_active = stock_qty > 0
                    except (ValueError, TypeError):
                        product.stock = 0
                        product.is_active = False
                    
                    # Зберігаємо
                    product.save(update_fields=['retail_price', 'stock', 'is_active'])
                    updated_count += 1
                    
                    # Виводимо прогрес кожні 100 товарів
                    if updated_count % 100 == 0:
                        self.stdout.write(f'  Оновлено {updated_count} товарів...')
                    
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'  Помилка обробки рядка: {e}'))
            
            # Підсумок
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('✓ Оновлення завершено!'))
            self.stdout.write(f'  Оновлено товарів: {updated_count}')
            if not_found_count > 0:
                self.stdout.write(self.style.WARNING(f'  Не знайдено в базі: {not_found_count}'))
            if error_count > 0:
                self.stdout.write(self.style.WARNING(f'  Помилок: {error_count}'))
            self.stdout.write(self.style.SUCCESS('='*60))
            
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Помилка завантаження CSV: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Непередбачена помилка: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())

