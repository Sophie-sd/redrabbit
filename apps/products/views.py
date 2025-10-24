from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Product, Category, ProductAttribute


class CategoryView(ListView):
    model = Product
    template_name = 'products/category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        
        if self.category.children.filter(is_active=True).exists():
            return Product.objects.none()
        
        return Product.objects.filter(
            category=self.category, 
            is_active=True
        ).prefetch_related('attributes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['subcategories'] = self.category.children.filter(is_active=True, slug__isnull=False).exclude(slug='')
        
        if not context['subcategories']:
            products_in_category = Product.objects.filter(
                category=self.category,
                is_active=True
            )
            
            brands = products_in_category.exclude(vendor_name='').values('vendor_name').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            context['available_brands'] = [b['vendor_name'] for b in brands]
            
            power_types = ProductAttribute.objects.filter(
                product__category=self.category,
                product__is_active=True,
                name='Живлення'
            ).values('value').annotate(count=Count('id')).order_by('-count')
            context['available_power'] = [p['value'] for p in power_types if p['value']]
            
            waterproof_types = ProductAttribute.objects.filter(
                product__category=self.category,
                product__is_active=True,
                name='Водостійкість'
            ).values('value').annotate(count=Count('id')).order_by('-count')
            context['available_waterproof'] = [w['value'] for w in waterproof_types if w['value']]
            
            vibration_types = ProductAttribute.objects.filter(
                product__category=self.category,
                product__is_active=True,
                name='Вібрація'
            ).values('value').annotate(count=Count('id')).order_by('-count')
            context['available_vibration'] = [v['value'] for v in vibration_types if v['value']]
        
        return context


class ProductDetailView(DetailView):
    """Детальна сторінка товару"""
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True)


class SaleProductsView(ListView):
    """Акції - показує товари з is_sale=True АБО товари з PromotionProduct"""
    model = Product
    template_name = 'products/sale.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        from .models import PromotionProduct
        from django.db.models import Q
        
        # Отримуємо ID товарів з PromotionProduct
        promo_product_ids = PromotionProduct.objects.filter(
            is_active=True
        ).values_list('product_id', flat=True)
        
        # Показуємо товари де is_sale=True АБО товар є в PromotionProduct
        return Product.objects.filter(
            Q(is_sale=True) | Q(id__in=promo_product_ids),
            is_active=True
        ).prefetch_related('images').distinct().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import PromotionProduct
        
        # Створюємо словник з PromotionProduct для швидкого доступу
        promo_products = PromotionProduct.objects.filter(
            is_active=True
        ).select_related('product')
        
        promo_dict = {pp.product_id: pp for pp in promo_products}
        context['promo_dict'] = promo_dict
        
        return context
