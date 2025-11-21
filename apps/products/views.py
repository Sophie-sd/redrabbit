from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Prefetch
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
import logging
from .models import Product, Category

logger = logging.getLogger(__name__)


@method_decorator(cache_page(60 * 5), name='dispatch')  # Кеш на 5 хвилин
class CategoryView(ListView):
    model = Product
    template_name = 'products/category.html'
    context_object_name = 'products'
    paginate_by = 15
    
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
        
        # Мін/Макс ціна для фільтру (ОПТИМІЗОВАНО - використовуємо aggregate)
        from django.db.models import Min, Max
        price_range = self.get_queryset().aggregate(
            min_price=Min('retail_price'),
            max_price=Max('retail_price')
        )
        context['min_price'] = int(price_range['min_price']) if price_range['min_price'] else 0
        context['max_price'] = int(price_range['max_price']) if price_range['max_price'] else 10000
        
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


@csrf_exempt
@require_POST
def trigger_sync(request):
    """Endpoint для тригеру синхронізації (для cron-job.org)"""
    secret = request.POST.get('secret', '')
    
    if secret != getattr(settings, 'CRON_SECRET', 'change-me'):
        logger.warning(f'Unauthorized cron attempt from {request.META.get("REMOTE_ADDR")}')
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        logger.info('Starting sync from cron trigger')
        call_command('sync_products', '--skip-images')
        call_command('update_prices_xls')
        logger.info('Sync completed successfully')
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f'Sync error: {e}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
