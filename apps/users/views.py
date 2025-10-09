"""
Views для користувачів
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, View, FormView
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib import messages
from .models import CustomUser
from .forms import WholesaleRegistrationForm, CustomLoginForm
from .utils import send_verification_email


class WholesaleRegisterView(CreateView):
    """Реєстрація тільки для оптових клієнтів"""
    
    model = CustomUser
    form_class = WholesaleRegistrationForm
    template_name = 'users/register.html'
    
    def form_valid(self, form):
        # Зберігаємо користувача (is_active=False)
        user = form.save()
        
        # Надсилаємо лист з підтвердженням
        if send_verification_email(user, self.request):
            messages.success(
                self.request, 
                'Ви успішно зареєструвалися! Перевірте вашу пошту для підтвердження email.'
            )
        else:
            messages.warning(
                self.request,
                'Реєстрація успішна, але виникла помилка при надсиланні листа. Зверніться до підтримки.'
            )
        
        return redirect('users:registration_pending')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Будь ласка, виправте помилки у формі.')
        return super().form_invalid(form)


class RegistrationPendingView(TemplateView):
    """Сторінка після реєстрації - очікування підтвердження email"""
    template_name = 'users/registration_pending.html'


class EmailVerificationView(View):
    """Підтвердження email через токен"""
    
    def get(self, request, token):
        # Шукаємо користувача з таким токеном
        try:
            user = CustomUser.objects.get(email_verification_token=token)
            
            # Верифікуємо email
            if user.verify_email(token):
                # Логінимо користувача
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                messages.success(
                    request,
                    'Email успішно підтверджено! Тепер вам доступні оптові ціни після входу.'
                )
                return redirect('users:profile')
            else:
                messages.error(request, 'Невірний токен верифікації.')
                return redirect('users:login')
                
        except CustomUser.DoesNotExist:
            messages.error(request, 'Невірний токен верифікації або токен вже використано.')
            return redirect('users:login')


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


class CustomLoginView(DjangoLoginView):
    """Custom login view з покращеною валідацією"""
    
    form_class = CustomLoginForm
    template_name = 'users/login.html'
    
    def form_invalid(self, form):
        # Додаємо кастомні повідомлення про помилки
        username = form.data.get('username', '')
        
        if username:
            # Перевіряємо чи існує користувач з таким email
            user_exists = CustomUser.objects.filter(email=username).exists() or \
                         CustomUser.objects.filter(username=username).exists()
            
            if not user_exists:
                messages.error(
                    self.request,
                    'Користувача з такими даними не зареєстровано. Будь ласка, зареєструйтеся.'
                )
            else:
                messages.error(
                    self.request,
                    'Невірний пароль. Перевірте правильність введення паролю.'
                )
        
        return super().form_invalid(form)
