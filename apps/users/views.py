"""
Views для користувачів
"""
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import CustomUser
from .forms import WholesaleRegistrationForm


class WholesaleRegisterView(CreateView):
    """Реєстрація тільки для оптових клієнтів"""
    
    model = CustomUser
    form_class = WholesaleRegistrationForm
    template_name = 'users/register.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request, 
            'Ви успішно зареєструвалися! Оптові ціни будуть доступні після досягнення обороту 5000₴ за місяць.'
        )
        return redirect('users:profile')


class ProfileView(LoginRequiredMixin, TemplateView):
    """Особистий кабінет користувача"""
    
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Оновлюємо статус користувача
        user.update_wholesale_status()
        
        context.update({
            'user': user,
            'monthly_turnover': user.monthly_turnover,
            'is_wholesale': user.is_wholesale,
            'turnover_to_wholesale': max(0, 5000 - float(user.monthly_turnover)),
        })
        return context


class UserOrdersView(LoginRequiredMixin, TemplateView):
    """Замовлення користувача"""
    
    template_name = 'users/orders.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.orders.models import Order
        
        context['orders'] = Order.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
        return context
