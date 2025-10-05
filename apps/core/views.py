"""
Core Views - основні представлення сайту
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q
from apps.products.models import Product, Category, RecommendedProduct
from apps.blog.models import Article


class HomeView(TemplateView):
    """Головна сторінка"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отримуємо рекомендовані товари
        recommended_products = RecommendedProduct.objects.filter(
            is_active=True,
            product__is_active=True
        ).select_related('product')[:10]
        
        context.update({
            'recommended_products': [rp.product for rp in recommended_products],
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
        query = self.request.GET.get('q', '')
        
        if query:
            products = Product.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(category__name__icontains=query),
                is_active=True
            ).distinct()[:20]
            context.update({
                'products': products,
                'query': query,
                'results_count': products.count() if products else 0,
            })
        
        return context
