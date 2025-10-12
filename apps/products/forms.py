"""
Форми для адмін-панелі товарів з валідацією
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Product


class ProductAdminForm(forms.ModelForm):
    """Форма додавання/редагування товару з валідацією"""
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def clean(self):
        """Загальна валідація форми"""
        cleaned_data = super().clean()
        
        retail_price = cleaned_data.get('retail_price')
        wholesale_price = cleaned_data.get('wholesale_price')
        sale_price = cleaned_data.get('sale_price')
        price_3_qty = cleaned_data.get('price_3_qty')
        price_5_qty = cleaned_data.get('price_5_qty')
        is_sale = cleaned_data.get('is_sale')
        stock = cleaned_data.get('stock')
        is_active = cleaned_data.get('is_active')
        
        # Перевірка оптової ціни
        if wholesale_price and retail_price:
            if wholesale_price >= retail_price:
                raise ValidationError({
                    'wholesale_price': 'Оптова ціна повинна бути меншою за роздрібну ціну'
                })
        
        # Перевірка акційної ціни
        if is_sale:
            if not sale_price:
                raise ValidationError({
                    'sale_price': 'Вкажіть акційну ціну, якщо товар позначено як акційний'
                })
            if sale_price >= retail_price:
                raise ValidationError({
                    'sale_price': 'Акційна ціна повинна бути меншою за роздрібну ціну'
                })
        
        # Перевірка градації цін
        if price_3_qty and retail_price:
            if price_3_qty >= retail_price:
                raise ValidationError({
                    'price_3_qty': 'Ціна "від 3 шт" повинна бути меншою за роздрібну ціну'
                })
        
        if price_5_qty and retail_price:
            if price_5_qty >= retail_price:
                raise ValidationError({
                    'price_5_qty': 'Ціна "від 5 шт" повинна бути меншою за роздрібну ціну'
                })
        
        if price_3_qty and price_5_qty:
            if price_5_qty >= price_3_qty:
                raise ValidationError({
                    'price_5_qty': 'Ціна "від 5 шт" повинна бути меншою за ціну "від 3 шт"'
                })
        
        # Попередження про активний товар без наявності
        if is_active and stock == 0:
            self.add_error('stock', 'Увага: товар активний, але кількість на складі = 0. Клієнти не зможуть його замовити.')
        
        return cleaned_data
    
    def clean_retail_price(self):
        """Валідація роздрібної ціни"""
        price = self.cleaned_data.get('retail_price')
        if price and price <= 0:
            raise ValidationError('Роздрібна ціна повинна бути більшою за 0')
        return price
    
    def clean_sku(self):
        """Валідація артикулу"""
        sku = self.cleaned_data.get('sku')
        if sku:
            sku = sku.strip().upper()
        return sku

