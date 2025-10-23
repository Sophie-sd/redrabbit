"""
Оптимізована команда для масового завантаження картинок
"""
import xml.etree.ElementTree as ET
import requests
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import Product
from apps.products.utils import download_product_images


class Command(BaseCommand):
    help = 'Масове завантаження картинок для товарів без зображень'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
            help='URL XML фіду'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Розмір пакету для обробки (за замовчуванням: 100)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.1,
            help='Затримка між завантаженнями в секундах (за замовчуванням: 0.1)'
        )
        parser.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Максимальна кількість повторних спроб'
        )

    def handle(self, *args, **options):
        url = options['url']
        batch_size = options['batch_size']
        delay = options['delay']
        max_retries = options['max_retries']

        self.stdout.write(self.style.SUCCESS('🖼️  МАСОВЕ ЗАВАНТАЖЕННЯ КАРТИНОК'))
        self.stdout.write('='*60)

        # Знаходимо товари без картинок
        products_without_images = Product.objects.filter(
            images__isnull=True,
            is_active=True,
            external_id__isnull=False
        ).distinct()
        
        total_products = products_without_images.count()
        self.stdout.write(f'Знайдено {total_products} товарів без картинок')
        
        if total_products == 0:
            self.stdout.write(self.style.SUCCESS('✅ Всі товари вже мають картинки'))
            return

        try:
            # Завантажуємо XML з картинками
            self.stdout.write(f'\n📥 Завантаження XML з {url}...')
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            # Створюємо індекс картинок по vendor_code
            offers_elem = root.find('.//offers')
            if not offers_elem:
                self.stdout.write(self.style.ERROR('❌ Не знайдено offers в XML'))
                return

            self.stdout.write('🗂️  Створення індексу картинок...')
            images_index = {}
            
            for offer in offers_elem.findall('offer'):
                vendor_code = self._get_text(offer, 'vendorCode')
                if vendor_code:
                    pictures = offer.findall('picture')
                    if pictures:
                        images_index[vendor_code] = [p.text for p in pictures if p.text]

            self.stdout.write(f'Знайдено картинки для {len(images_index)} товарів')

            # Обробляємо товари пакетами
            processed = 0
            downloaded = 0
            skipped = 0
            errors = 0

            for i in range(0, total_products, batch_size):
                batch = products_without_images[i:i + batch_size]
                
                self.stdout.write(f'\n📦 Пакет {i//batch_size + 1}: товари {i+1}-{min(i+batch_size, total_products)}')
                
                with transaction.atomic():
                    for product in batch:
                        if not product.external_id:
                            skipped += 1
                            continue

                        picture_urls = images_index.get(product.external_id, [])
                        if not picture_urls:
                            skipped += 1
                            continue

                        # Завантажуємо картинки з повторними спробами
                        success = False
                        for retry in range(max_retries):
                            try:
                                success_count, error_count = download_product_images(
                                    product, 
                                    picture_urls, 
                                    clear_existing=False
                                )
                                
                                if success_count > 0:
                                    downloaded += 1
                                    success = True
                                    break
                                elif error_count > 0:
                                    errors += error_count
                                    
                            except Exception as e:
                                if retry == max_retries - 1:
                                    self.stdout.write(f'    ❌ {product.name}: {e}')
                                    errors += 1
                                else:
                                    time.sleep(delay * (retry + 1))  # Збільшуємо затримку з кожною спробою

                        if not success:
                            skipped += 1

                        processed += 1
                        
                        # Затримка між товарами
                        if delay > 0:
                            time.sleep(delay)

                    # Прогрес
                    self.stdout.write(f'    ✅ Оброблено: {processed}/{total_products} '
                                    f'(завантажено: {downloaded}, пропущено: {skipped})')

            # Підсумок
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('🎉 ЗАВАНТАЖЕННЯ ЗАВЕРШЕНО!'))
            self.stdout.write(f'📊 Загальна статистика:')
            self.stdout.write(f'   • Оброблено товарів: {processed}')
            self.stdout.write(f'   • Завантажено картинок: {downloaded}')
            self.stdout.write(f'   • Пропущено: {skipped}')
            if errors > 0:
                self.stdout.write(self.style.WARNING(f'   • Помилок: {errors}'))
            self.stdout.write('='*60)

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'❌ Помилка завантаження XML: {e}'))
        except ET.ParseError as e:
            self.stdout.write(self.style.ERROR(f'❌ Помилка парсингу XML: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Непередбачена помилка: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())

    def _get_text(self, element, tag):
        """Безпечно отримує текст з XML елемента"""
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return ''
