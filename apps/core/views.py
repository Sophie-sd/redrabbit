"""
Core Views - основні представлення сайту
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Q
from django.db import connection
from apps.products.models import Product, Category, ProductReview
from .models import Banner

# PostgreSQL Full-Text Search (якщо доступний)
try:
    from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False



class HomeView(TemplateView):
    """Головна сторінка"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отримуємо активні банери
        banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')
        
        # Отримуємо акційні товари (тільки з АКТИВНИМИ акціями)
        from django.utils import timezone
        now = timezone.now()
        
        from apps.products.models import ProductImage
        
        sale_products = Product.objects.filter(
            is_active=True,
            is_sale=True,
            sale_price__isnull=False
        ).filter(
            Q(sale_start_date__isnull=True) | Q(sale_start_date__lte=now)
        ).filter(
            Q(sale_end_date__isnull=True) | Q(sale_end_date__gt=now)
        ).select_related('primary_category').prefetch_related(
            Prefetch('images',
                queryset=ProductImage.objects.filter(is_main=True).only('image', 'is_main', 'product_id'),
                to_attr='main_images'
            )
        ).order_by('sort_order', '-created_at')[:20]
        
        from apps.products.models import TopProduct
        top_product_entries = TopProduct.objects.filter(
            is_active=True,
            product__is_active=True
        ).select_related('product__primary_category').prefetch_related(
            Prefetch('product__images',
                queryset=ProductImage.objects.filter(is_main=True).only('image', 'is_main', 'product_id'),
                to_attr='main_images'
            )
        ).order_by('sort_order', '-created_at')[:12]
        
        top_products = [entry.product for entry in top_product_entries]
        
        # Отримуємо схвалені відгуки
        reviews = ProductReview.objects.filter(
            is_approved=True
        ).select_related('product').prefetch_related('product__images').order_by('-created_at')[:10]
        
        context.update({
            'banners': banners,
            'sale_products': sale_products,
            'top_products': top_products,
            'reviews': reviews,
            'categories': Category.objects.filter(parent=None, is_active=True).order_by('sort_order', 'name'),
        })
        return context


class DeliveryView(TemplateView):
    """Доставка та оплата"""
    template_name = 'core/delivery.html'


class ReturnsView(TemplateView):
    """Повернення та обмін"""
    template_name = 'core/returns.html'


class AboutView(TemplateView):
    """Про нас"""
    template_name = 'core/about.html'


class ContactsView(TemplateView):
    """Контакти"""
    template_name = 'core/contacts.html'


class TermsView(TemplateView):
    """Умови використання"""
    template_name = 'core/terms.html'


class PrivacyView(TemplateView):
    """Політика конфіденційності"""
    template_name = 'core/privacy.html'


class SearchView(TemplateView):
    """Пошук товарів - оптимізований з кешуванням"""
    template_name = 'core/search.html'
    
    def get_context_data(self, **kwargs):
        from django.core.cache import cache
        
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        if query:
            # Перевіряємо кеш
            cache_key = f'search_initial:{query.lower()}'
            cached_data = cache.get(cache_key)
            
            if cached_data:
                context.update(cached_data)
            else:
                # Визначаємо тип БД
                db_engine = connection.settings_dict['ENGINE']
                use_postgres = 'postgresql' in db_engine and POSTGRES_AVAILABLE
                
                if use_postgres:
                    # PostgreSQL з триграмами
                    from django.contrib.postgres.search import TrigramSimilarity
                    
                    products = Product.objects.filter(
                        is_active=True
                    ).annotate(
                        similarity=TrigramSimilarity('name', query),
                    ).filter(
                        Q(similarity__gt=0.1) |
                        Q(name__icontains=query) |
                        Q(description__icontains=query)
                    ).order_by('-similarity').select_related('primary_category').only(
                        'id', 'name', 'slug', 'retail_price', 'sale_price', 'is_sale',
                        'sale_start_date', 'sale_end_date', 'is_top', 'is_new',
                        'primary_category__name', 'primary_category__slug'
                    ).distinct()[:20]  # Завантажуємо одразу 20 товарів
                else:
                    # SQLite fallback
                    products = Product.objects.filter(
                        Q(name__icontains=query) | 
                        Q(description__icontains=query) |
                        Q(primary_category__name__icontains=query),
                        is_active=True
                    ).select_related('primary_category').only(
                        'id', 'name', 'slug', 'retail_price', 'sale_price', 'is_sale',
                        'sale_start_date', 'sale_end_date', 'is_top', 'is_new',
                        'primary_category__name', 'primary_category__slug'
                    ).distinct()[:20]
                
                data = {
                    'products': products,
                    'query': query,
                    'initial_count': len(products),
                }
                
                # Кешуємо на 5 хвилин
                cache.set(cache_key, data, 300)
                context.update(data)
        
        return context


def search_autocomplete(request):
    """API для автокомпліту пошуку - оптимізований"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    try:
        from apps.products.models import ProductImage
        
        db_engine = connection.settings_dict['ENGINE']
        use_postgres_search = 'postgresql' in db_engine and POSTGRES_AVAILABLE
        
        if use_postgres_search:
            from django.contrib.postgres.search import TrigramSimilarity
            
            products = Product.objects.filter(
                is_active=True,
                name__icontains=query
            ).annotate(
                similarity=TrigramSimilarity('name', query),
            ).filter(
                similarity__gt=0.3
            ).order_by('-similarity').select_related('primary_category').prefetch_related(
                Prefetch('images', 
                    queryset=ProductImage.objects.filter(is_main=True).only('image', 'is_main'),
                    to_attr='main_images'
                )
            ).only(
                'id', 'name', 'slug', 'retail_price', 'sale_price', 'is_sale', 
                'sale_start_date', 'sale_end_date'
            )[:5]
        else:
            products = Product.objects.filter(
                name__icontains=query,
                is_active=True
            ).select_related('primary_category').prefetch_related(
                Prefetch('images',
                    queryset=ProductImage.objects.filter(is_main=True).only('image', 'is_main'),
                    to_attr='main_images'
                )
            ).only(
                'id', 'name', 'slug', 'retail_price', 'sale_price', 'is_sale',
                'sale_start_date', 'sale_end_date'
            )[:5]
        
        results = []
        for p in products:
            image_url = None
            if hasattr(p, 'main_images') and p.main_images:
                image_url = p.main_images[0].image.url if p.main_images[0].image else None
            
            price = p.sale_price if (p.is_sale and p.sale_price) else p.retail_price
            
            results.append({
                'name': p.name,
                'url': p.get_absolute_url(),
                'price': str(int(price)),
                'image': image_url
            })
        
        return JsonResponse({'results': results})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Search autocomplete error: {e}')
        return JsonResponse({'results': [], 'error': str(e)}, status=500)


def search_paginated(request):
    """API для пагінованого пошуку - оптимізований з кешуванням"""
    from django.core.cache import cache
    
    query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))
    
    if not query:
        return JsonResponse({'error': 'Query required'}, status=400)
    
    # Перевіряємо кеш
    cache_key = f'search:{query.lower()}:page{page}:per{per_page}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return JsonResponse(cached_result)
    
    try:
        # Визначаємо тип БД
        db_engine = connection.settings_dict['ENGINE']
        use_postgres_search = 'postgresql' in db_engine and POSTGRES_AVAILABLE
        
        if use_postgres_search:
            # PostgreSQL Full-Text Search з триграмами для кращої продуктивності
            from django.contrib.postgres.search import TrigramSimilarity
            
            base_queryset = Product.objects.filter(
                is_active=True
            ).annotate(
                similarity=TrigramSimilarity('name', query),
            ).filter(
                Q(similarity__gt=0.1) |  # Пошук по схожості назви
                Q(name__icontains=query) |  # Резервний пошук
                Q(description__icontains=query)
            ).order_by('-similarity', '-created_at').select_related('primary_category').only(
                'id', 'name', 'slug', 'retail_price', 'sale_price', 'is_sale',
                'sale_start_date', 'sale_end_date', 'is_top', 'is_new',
                'primary_category__name', 'primary_category__slug'
            ).distinct()
        else:
            # SQLite fallback
            base_queryset = Product.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(primary_category__name__icontains=query),
                is_active=True
            ).select_related('primary_category').only(
                'id', 'name', 'slug', 'retail_price', 'sale_price', 'is_sale',
                'sale_start_date', 'sale_end_date', 'is_top', 'is_new',
                'primary_category__name', 'primary_category__slug'
            ).distinct()
        
        # Загальна кількість (кешуємо окремо)
        count_cache_key = f'search_count:{query.lower()}'
        total_count = cache.get(count_cache_key)
        if total_count is None:
            total_count = base_queryset.count()
            cache.set(count_cache_key, total_count, 300)  # 5 хвилин
        
        # Пагінація
        offset = (page - 1) * per_page
        products = base_queryset[offset:offset + per_page]
        
        # Формуємо результати
        results = []
        for p in products:
            # Отримуємо тільки головне зображення без додаткових запитів
            image_url = None
            try:
                main_image = p.images.filter(is_main=True).only('image').first()
                if not main_image:
                    main_image = p.images.only('image').first()
                if main_image and main_image.image:
                    image_url = main_image.image.url
            except:
                pass
            
            # Визначаємо ціну
            price = p.sale_price if (p.is_sale and p.sale_price) else p.retail_price
            
            results.append({
                'id': p.id,
                'name': p.name,
                'url': p.get_absolute_url(),
                'price': str(int(price)),
                'image': image_url,
                'category': p.primary_category.name if p.primary_category else '',
                'is_sale': p.is_sale_active(),
                'is_top': p.is_top,
                'is_new': p.is_new,
            })
        
        # Підраховуємо сторінки
        total_pages = (total_count + per_page - 1) // per_page
        
        response_data = {
            'products': results,
            'total_count': total_count,
            'current_page': page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
        }
        
        # Кешуємо результат на 5 хвилин
        cache.set(cache_key, response_data, 300)
        
        return JsonResponse(response_data)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Search paginated error: {e}')
        return JsonResponse({'error': str(e)}, status=500)
