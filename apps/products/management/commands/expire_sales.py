"""
Management command для автоматичного завершення акцій
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.products.models import Product


class Command(BaseCommand):
    help = 'Автоматично завершує акції, термін дії яких закінчився'

    def handle(self, *args, **options):
        now = timezone.now()
        
        expired_products = Product.objects.filter(
            is_sale=True,
            sale_end_date__lte=now
        )
        
        expired_names = list(expired_products.values_list('name', flat=True))
        count = len(expired_names)
        
        if count > 0:
            expired_products.update(
                is_sale=False,
                sale_price=None,
                sale_name='',
                sale_start_date=None,
                sale_end_date=None
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Завершено {count} акцій')
            )
            
            for name in expired_names:
                self.stdout.write(f'  - {name}')
        else:
            self.stdout.write(
                self.style.SUCCESS('✓ Немає акцій для завершення')
            )

