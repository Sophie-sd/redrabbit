"""
Core Views - основні представлення сайту
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Q
from django.db import connection
from apps.products.models import Product, Category
from .models import Banner

# Безпечний імпорт Brand та ProductReview
try:
    from apps.products.models import Brand, ProductReview
    BRAND_REVIEW_AVAILABLE = True
except Exception:
    BRAND_REVIEW_AVAILABLE = False


class HomeView(TemplateView):
    """Головна сторінка"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отримуємо активні банери
        banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')
        
        # Отримуємо акційні товари (товари з бейджем АКЦІЯ)
        sale_products = Product.objects.filter(
            is_active=True,
            is_sale=True,
            sale_price__isnull=False
        ).select_related('category').prefetch_related('images').order_by('sort_order', '-created_at')[:20]
        
        # Отримуємо хіти (товари з бейджем ХІТ)
        top_products = Product.objects.filter(
            is_active=True,
            is_top=True
        ).select_related('category').prefetch_related('images').order_by('sort_order', '-created_at')[:12]
        
        # Бренди (топ-8) - безпечний запит з перевіркою таблиці
        brands = []
        if BRAND_REVIEW_AVAILABLE:
            try:
                # Перевіряємо чи існує таблиця
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM products_brand LIMIT 1")
                brands = Brand.objects.filter(is_active=True).order_by('sort_order', 'name')[:8]
            except Exception:
                brands = []
        
        # Відгуки (схвалені, топ-10) - безпечний запит з перевіркою таблиці
        reviews = []
        if BRAND_REVIEW_AVAILABLE:
            try:
                # Перевіряємо чи існує таблиця
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM products_productreview LIMIT 1")
                reviews = ProductReview.objects.filter(
                    is_approved=True
                ).select_related('product').prefetch_related('product__images').order_by('-created_at')[:10]
            except Exception:
                reviews = []
        
        context.update({
            'banners': banners,
            'sale_products': sale_products,
            'top_products': top_products,
            'brands': brands,
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
    """Пошук товарів"""
    template_name = 'core/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        if query:
            # Спочатку отримуємо всі результати для підрахунку
            all_products = Product.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(category__name__icontains=query),
                is_active=True
            ).distinct()
            
            # Підраховуємо загальну кількість
            total_count = all_products.count()
            
            # Берем тільки перші 20 для відображення
            products = all_products[:20]
            
            context.update({
                'products': products,
                'query': query,
                'results_count': total_count,
            })
        
        return context


def search_autocomplete(request):
    """API для автокомпліту пошуку"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    try:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        ).select_related('category').prefetch_related('images')[:5]
        
        results = []
        for p in products:
            image_url = None
            if p.images.exists():
                first_image = p.images.first()
                if first_image and hasattr(first_image, 'image'):
                    image_url = first_image.image.url if first_image.image else None
            
            results.append({
                'name': p.name,
                'url': p.get_absolute_url(),
                'price': str(int(p.retail_price)),
                'image': image_url
            })
        
        return JsonResponse({'results': results})
    except Exception as e:
        return JsonResponse({'results': [], 'error': str(e)}, status=500)
