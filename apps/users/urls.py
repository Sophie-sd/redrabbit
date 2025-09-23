"""
URLs для користувачів
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Реєстрація тільки для оптових клієнтів
    path('register/', views.WholesaleRegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Особистий кабінет
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('orders/', views.UserOrdersView.as_view(), name='orders'),
]
