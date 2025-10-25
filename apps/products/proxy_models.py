"""
Proxy моделі для зручного управління в адмінці
"""
from .models import Product


class SaleProduct(Product):
    """Proxy модель для управління акційними товарами"""
    
    class Meta:
        proxy = True
        verbose_name = 'Акційна пропозиція'
        verbose_name_plural = 'Акційні пропозиції'

