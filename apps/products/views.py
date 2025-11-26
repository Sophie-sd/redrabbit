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
        
        # Крок 1: Отримуємо категорію з оптимізованими prefetch
        self.category = get_object_or_404(
            Category.objects.select_related('parent').prefetch_related(
                Prefetch(
                    'children',
                    queryset=Category.objects.filter(is_active=True)
                )
            ),
            slug=self.kwargs['slug']
        )
        
        # Крок 2: Отримуємо дочірні категорії (з prefetch, БЕЗ додаткового запиту)
        child_categories = [
            child for child in self.category.children.all()
            if child.is_active
        ]
        
        # Крок 3: Будуємо base queryset з усіма оптимізаціями
        base_queryset = Product.objects.select_related(
            'primary_category'
        ).prefetch_related(
            'categories',  # ДОДАНО: запобігає N+1 для product.categories.all()
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(is_main=True).only('image', 'image_url', 'is_main', 'product_id'),
                to_attr='main_images'
            )
        ).only(
            'id', 'name', 'slug', 'retail_price', 'sale_price', 'is_sale',
            'sale_start_date', 'sale_end_date', 'primary_category__name', 'created_at',
            'stock'  # ДОДАНО: потрібно для product.is_in_stock()
        )
        
        # Крок 4: Фільтруємо товари
        if child_categories:
            child_ids = [child.id for child in child_categories]
            
            return base_queryset.filter(
                Q(categories__id=self.category.id) | 
                Q(primary_category__id=self.category.id) |
                Q(categories__id__in=child_ids) | 
                Q(primary_category__id__in=child_ids),
                is_active=True,
                stock__gt=0
            ).distinct()
        
        return base_queryset.filter(
            Q(categories__id=self.category.id) | Q(primary_category__id=self.category.id),
            is_active=True,
            stock__gt=0
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        
        # Використовуємо вже завантажені дані з prefetch
        subcategories = [
            child for child in self.category.children.all()
            if child.is_active
        ]
        context['subcategories'] = subcategories
        
        if subcategories:
            context['available_subcategories'] = subcategories
        
        # Оптимізація: використовуємо object_list (вже завантажені товари) замість повторного get_queryset()
        products = context.get('object_list', [])
        if products:
            # Рахуємо мін/макс ціну в Python (швидше ніж aggregate для сторінки з 15 товарів)
            prices = [p.get_current_price() for p in products if p.get_current_price()]
            context['min_price'] = int(min(prices)) if prices else 0
            context['max_price'] = int(max(prices)) if prices else 10000
        else:
            context['min_price'] = 0
            context['max_price'] = 10000
        
        return context


class ProductDetailView(DetailView):
    """Детальна сторінка товару"""
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        from .models import ProductImage
        return Product.objects.filter(is_active=True, stock__gt=0).prefetch_related(
            Prefetch('images',
                queryset=ProductImage.objects.only('image', 'image_url', 'is_main', 'alt_text', 'product_id').order_by('sort_order', 'id')
            )
        )


@method_decorator(cache_page(60 * 5), name='dispatch')
class SaleProductsView(ListView):
    """Акції - показує товари з активними акціями"""
    model = Product
    template_name = 'products/sale.html'
    context_object_name = 'products'
    paginate_by = 15
    
    def get_queryset(self):
        from .models import ProductImage
        
        return Product.objects.filter(
            is_sale=True,
            sale_price__isnull=False,
            is_active=True,
            stock__gt=0
        ).select_related('primary_category').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(is_main=True).only('image', 'image_url', 'is_main', 'product_id'),
                to_attr='main_images'
            )
        ).only(
            'id', 'name', 'slug', 'retail_price', 'sale_price', 'is_sale',
            'sale_start_date', 'sale_end_date', 'primary_category__name', 'stock'
        ).order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # total_products видалено - не використовується в template
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
