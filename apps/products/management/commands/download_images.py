"""
Команда для довантаження зображень для існуючих товарів
"""
import xml.etree.ElementTree as ET
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.products.models import Product, ProductImage


class Command(BaseCommand):
    help = 'Завантажує зображення для товарів, що не мають зображень'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://smtm.com.ua/_prices/import-retail-ua-2.xml',
            help='URL XML фіду'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Максимальна кількість товарів'
        )
        parser.add_argument(
            '--redownload',
            action='store_true',
            help='Перезавантажити зображення навіть якщо вони є'
        )

    def handle(self, *args, **options):
        url = options['url']
        limit = options['limit']
        redownload = options['redownload']

        self.stdout.write(f'Завантаження XML з {url}...')

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            offers_elem = root.find('.//offers')
            if not offers_elem:
                self.stdout.write(self.style.ERROR('Не знайдено offers в XML'))
                return

            offers = offers_elem.findall('offer')
            
            if limit:
                offers = offers[:limit]
            
            total = len(offers)
            self.stdout.write(f'Знайдено {total} товарів в XML')

            processed = 0
            downloaded = 0
            skipped = 0
            errors = 0

            for idx, offer in enumerate(offers, 1):
                try:
                    vendor_code = self._get_text(offer, 'vendorCode')
                    if not vendor_code:
                        continue

                    product = Product.objects.filter(external_id=vendor_code).first()
                    if not product:
                        skipped += 1
                        continue

                    has_images = product.images.exists()
                    
                    if has_images and not redownload:
                        skipped += 1
                        continue

                    pictures = offer.findall('picture')
                    if not pictures:
                        skipped += 1
                        continue

                    if has_images and redownload:
                        product.images.all().delete()

                    img_count = 0
                    for pic_idx, picture in enumerate(pictures):
                        picture_url = picture.text
                        if not picture_url:
                            continue

                        try:
                            img_response = requests.get(picture_url, timeout=10)
                            img_response.raise_for_status()

                            file_name = picture_url.split('/')[-1]

                            ProductImage.objects.create(
                                product=product,
                                image=ContentFile(img_response.content, name=file_name),
                                is_main=(pic_idx == 0),
                                sort_order=pic_idx,
                            )
                            img_count += 1
                        except Exception as e:
                            self.stdout.write(f'  Помилка: {picture_url[:50]}... - {e}')
                            errors += 1

                    if img_count > 0:
                        downloaded += 1
                        processed += 1

                    if idx % 100 == 0:
                        self.stdout.write(f'  Оброблено {idx}/{total}... (завантажено: {downloaded})')

                except Exception as e:
                    errors += 1
                    self.stdout.write(f'  ✗ Помилка: {e}')

            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('✓ Завантаження завершено!'))
            self.stdout.write(f'  Товарів з новими зображеннями: {downloaded}')
            self.stdout.write(f'  Пропущено: {skipped}')
            if errors > 0:
                self.stdout.write(self.style.WARNING(f'  Помилок: {errors}'))
            self.stdout.write(self.style.SUCCESS('='*60))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Помилка: {e}'))

    def _get_text(self, element, tag):
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return ''

