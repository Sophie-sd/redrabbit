"""
Кошик покупок без реєстрації (session-based)
"""
from decimal import Decimal
from django.conf import settings
from apps.products.models import Product


class Cart:
    """Кошик покупок"""
    
    def __init__(self, request):
        """Ініціалізація кошика"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.user = request.user if request.user.is_authenticated else None
    
    def add(self, product, quantity=1, override_quantity=False):
        """Додавання товару в кошик"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.get_current_price())
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        # Оновлюємо ціну
        self.cart[product_id]['price'] = str(product.get_current_price())
        self.save()
    
    def save(self):
        """Зберігання кошика в сесії"""
        self.session.modified = True
    
    def remove(self, product):
        """Видалення товару з кошика"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        """Ітерація по товарах в кошику"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        """Кількість товарів в кошику"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """Загальна вартість кошика"""
        return sum(
            Decimal(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )
    
    def clear(self):
        """Очищення кошика"""
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def get_item_count(self):
        """Кількість позицій в кошику"""
        return len(self.cart)
    
    def update_quantities(self, product_quantities):
        """Оновлення кількості товарів"""
        for product_id, quantity in product_quantities.items():
            if product_id in self.cart:
                self.cart[product_id]['quantity'] = quantity
                if quantity <= 0:
                    del self.cart[product_id]
        self.save()
