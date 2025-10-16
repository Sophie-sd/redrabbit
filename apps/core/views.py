"""
Core Views - основні представлення сайту
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q
from apps.products.models import Product, Category
from .models import Banner


class HomeView(TemplateView):
    """Головна сторінка"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отримуємо активні банери
        banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')
        
        # Отримуємо новинки (товари з бейджем НОВИНКА)
        new_products = Product.objects.filter(
            is_active=True,
            is_new=True
        ).select_related('category').prefetch_related('images').order_by('sort_order', '-created_at')[:12]
        
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
        
        context.update({
            'banners': banners,
            'new_products': new_products,
            'sale_products': sale_products,
            'top_products': top_products,
            'categories': Category.objects.filter(parent=None, is_active=True).order_by('sort_order', 'name'),
        })
        return context


class CatalogView(TemplateView):
    """Каталог категорій"""
    template_name = 'core/catalog.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None, is_active=True).order_by('sort_order', 'name')
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
