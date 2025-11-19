from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Prefetch
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Product, Category


class CategoryView(ListView):
    model = Product
    template_name = 'products/category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        from .models import ProductImage
        
        children_with_products = Category.objects.filter(
            is_active=True
        ).annotate(
            products_count=Count('products', filter=Q(products__is_active=True), distinct=True) +
                           Count('primary_products', filter=Q(primary_products__is_active=True), distinct=True)
        ).filter(products_count__gt=0)
        
        self.category = get_object_or_404(
            Category.objects.select_related('parent').prefetch_related(
                Prefetch('children', queryset=children_with_products)
            ),
            slug=self.kwargs['slug']
        )
        
        child_categories = self.category.children.all()
        
        base_queryset = Product.objects.select_related(
            'primary_category'
        ).prefetch_related(
            Prefetch('images',
                queryset=ProductImage.objects.filter(is_main=True).only('image', 'is_main', 'product_id'),
                to_attr='main_images'
            )
        ).only(
            'id', 'name', 'slug', 'retail_price', 'sale_price', 'is_sale',
            'sale_start_date', 'sale_end_date', 'primary_category__name', 'created_at'
        )
        
        if child_categories.exists():
            child_ids = list(child_categories.values_list('id', flat=True))
            
            return base_queryset.filter(
                Q(categories__id=self.category.id) | 
                Q(primary_category__id=self.category.id) |
                Q(categories__id__in=child_ids) | 
                Q(primary_category__id__in=child_ids),
                is_active=True
            ).distinct()
        
        return base_queryset.filter(
            Q(categories__id=self.category.id) | Q(primary_category__id=self.category.id),
            is_active=True
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        
        subcategories = self.category.children.all()
        context['subcategories'] = subcategories
        
        if subcategories:
            context['available_subcategories'] = subcategories
        
        # Мін/Макс ціна для фільтру ціни
        if self.object_list:
            prices = self.object_list.values_list('retail_price', flat=True)
            context['min_price'] = int(min(prices)) if prices else 0
            context['max_price'] = int(max(prices)) if prices else 10000
        
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
    paginate_by = 15
    
    def get_queryset(self):
        return Product.objects.filter(
            is_sale=True,
            sale_price__isnull=False,
            is_active=True
        ).select_related('primary_category').prefetch_related('images').order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = self.get_queryset().count()
        return context