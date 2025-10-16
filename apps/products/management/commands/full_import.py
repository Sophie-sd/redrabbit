"""
Команда для повного імпорту: категорії + товари
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Виконує повний імпорт: спочатку категорії, потім товари'

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
            help='Максимальна кількість товарів для імпорту'
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Не завантажувати зображення товарів'
        )
        parser.add_argument(
            '--clear-categories',
            action='store_true',
            help='Видалити всі існуючі категорії перед імпортом'
        )

    def handle(self, *args, **options):
        url = options['url']
        limit = options['limit']
        skip_images = options['skip_images']
        clear_categories = options['clear_categories']

        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('ПОВНИЙ ІМПОРТ ДАНИХ ПОСТАЧАЛЬНИКА'))
        self.stdout.write(self.style.SUCCESS('='*60))

        # Крок 1: Імпорт категорій
        self.stdout.write(self.style.SUCCESS('\n[1/2] Імпорт категорій...'))
        self.stdout.write('-'*60)
        
        call_command(
            'import_categories',
            url=url,
            clear=clear_categories,
        )

        # Крок 2: Імпорт товарів
        self.stdout.write(self.style.SUCCESS('\n[2/2] Імпорт товарів...'))
        self.stdout.write('-'*60)
        
        import_options = {
            'url': url,
            'skip_images': skip_images,
        }
        
        if limit:
            import_options['limit'] = limit
        
        call_command('import_products', **import_options)

        # Фінальне повідомлення
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✓ ПОВНИЙ ІМПОРТ ЗАВЕРШЕНО!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        self.stdout.write('\nРекомендації:')
        self.stdout.write('  • Для регулярного оновлення цін використовуйте:')
        self.stdout.write('    python manage.py update_prices')
        self.stdout.write('  • Для оновлення існуючих товарів:')
        self.stdout.write('    python manage.py import_products --update-only')

