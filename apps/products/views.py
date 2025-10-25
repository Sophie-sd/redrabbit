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
            ).exclude(value='').values('value').distinct()
            context['available_power'] = sorted(set([p['value'] for p in power_types if p['value']]))
            
            waterproof_types = ProductAttribute.objects.filter(
                product__category=self.category,
                product__is_active=True,
                name='Водостійкість'
            ).exclude(value='').values('value').distinct()
            context['available_waterproof'] = sorted(set([w['value'] for w in waterproof_types if w['value']]))
            
            vibration_types = ProductAttribute.objects.filter(
                product__category=self.category,
                product__is_active=True,
                name='Вібрація'
            ).exclude(value='').values('value').distinct()
            context['available_vibration'] = sorted(set([v['value'] for v in vibration_types if v['value']]))

        
        return context


class ProductDetailView(DetailView):
    """Детальна сторінка товару"""
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True)


class SaleProductsView(ListView):
    """Акції - показує товари з активними акціями"""
    model = Product
    template_name = 'products/sale.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        return Product.objects.filter(
            is_sale=True,
            sale_price__isnull=False,
            is_active=True
        ).select_related('category').prefetch_related('images').order_by('-updated_at')
