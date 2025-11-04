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
        self.promo_code = self.session.get('promo_code', None)
    
    def add(self, product, quantity=1, override_quantity=False):
        """Додавання товару в кошик"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.get_current_price()),
                'retail_price': str(product.retail_price),
                'is_sale': product.is_sale_active()
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.cart[product_id]['price'] = str(product.get_current_price())
        self.cart[product_id]['retail_price'] = str(product.retail_price)
        self.cart[product_id]['is_sale'] = product.is_sale_active()
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
        
        products_dict = {str(p.id): p for p in products}
        
        for product_id, item_data in self.cart.items():
            product = products_dict.get(product_id)
            if not product:
                continue
            
            price = Decimal(item_data['price'])
            retail_price = Decimal(item_data.get('retail_price', item_data['price']))
            quantity = item_data['quantity']
            is_sale = item_data.get('is_sale', False)
            
            yield {
                'product': product,
                'price': price,
                'retail_price': retail_price,
                'quantity': quantity,
                'is_sale': is_sale,
                'total_price': price * quantity,
                'total_retail_price': retail_price * quantity,
                'discount_amount': (retail_price - price) * quantity if is_sale else Decimal('0')
            }
    
    def __len__(self):
        """Кількість товарів в кошику"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_subtotal(self):
        """Сума товарів без промокоду"""
        return sum(
            Decimal(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )
    
    def get_total_retail_price(self):
        """Сума всіх товарів за повною ціною"""
        return sum(
            Decimal(item.get('retail_price', item['price'])) * item['quantity'] 
            for item in self.cart.values()
        )
    
    def get_product_discount(self):
        """Загальна знижка від акційних цін"""
        return self.get_total_retail_price() - self.get_subtotal()
    
    def get_promo_discount(self):
        """Знижка від промокоду"""
        if not self.promo_code:
            return Decimal('0')
        
        from apps.orders.models import Promotion
        try:
            promotion = Promotion.objects.get(code=self.promo_code)
            if promotion.is_valid():
                subtotal = self.get_subtotal()
                
                applicable_total = Decimal('0')
                for item_data in self.cart.values():
                    try:
                        product = Product.objects.get(id=int(list(self.cart.keys())[list(self.cart.values()).index(item_data)]))
                        if promotion.can_apply_to_product(product):
                            applicable_total += Decimal(item_data['price']) * item_data['quantity']
                    except:
                        pass
                
                if applicable_total >= promotion.min_order_amount:
                    if promotion.discount_type == 'percentage':
                        discount = applicable_total * (promotion.discount_value / 100)
                    else:
                        discount = promotion.discount_value
                    return min(discount, applicable_total)
        except Promotion.DoesNotExist:
            pass
        
        return Decimal('0')
    
    def get_total_price(self):
        """Загальна вартість з урахуванням промокоду"""
        return max(self.get_subtotal() - self.get_promo_discount(), Decimal('0'))
    
    def apply_promo_code(self, code):
        """Застосувати промокод"""
        from apps.orders.models import Promotion
        try:
            promotion = Promotion.objects.get(code=code.upper())
            if promotion.is_valid():
                if self.get_subtotal() >= promotion.min_order_amount:
                    self.session['promo_code'] = code.upper()
                    self.promo_code = code.upper()
                    self.save()
                    return True, "Промокод успішно застосовано"
                else:
                    return False, f"Мінімальна сума замовлення для цього промокоду: {promotion.min_order_amount} ₴"
            else:
                return False, "Промокод недійсний або закінчився"
        except Promotion.DoesNotExist:
            return False, "Промокод не знайдено"
    
    def remove_promo_code(self):
        """Видалити промокод"""
        if 'promo_code' in self.session:
            del self.session['promo_code']
        self.promo_code = None
        self.save()
    
    def clear(self):
        """Очищення кошика"""
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
        self.remove_promo_code()
        self.save()
    
    def get_item_count(self):
        """Кількість позицій в кошику"""
        return len(self.cart)
    
    def update_quantities(self, product_quantities):
        """Оновлення кількості товарів"""
        for product_id, quantity in product_quantities.items():
            if product_id in self.cart:
                if quantity <= 0:
                    del self.cart[product_id]
                else:
                    self.cart[product_id]['quantity'] = quantity
        self.save()
