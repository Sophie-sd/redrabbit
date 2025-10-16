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
        sale_price = cleaned_data.get('sale_price')
        is_sale = cleaned_data.get('is_sale')
        stock = cleaned_data.get('stock')
        is_active = cleaned_data.get('is_active')
        
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
        
        # Попередження про активний товар без наявності
        if is_active and stock == 0:
            self.add_error('stock', 'Увага: товар активний, але кількість на складі = 0.')
        
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
            if self.instance.pk:
                if Product.objects.exclude(pk=self.instance.pk).filter(sku=sku).exists():
                    raise ValidationError(f'Товар з артикулом "{sku}" вже існує')
            else:
                if Product.objects.filter(sku=sku).exists():
                    raise ValidationError(f'Товар з артикулом "{sku}" вже існує')
        return sku
