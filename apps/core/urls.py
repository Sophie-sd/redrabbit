"""
Core URLs - основні сторінки сайту
"""
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('delivery/', views.DeliveryView.as_view(), name='delivery'),
    path('returns/', views.ReturnsView.as_view(), name='returns'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Нові юридичні сторінки
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    
]
