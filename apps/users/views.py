"""
Views для користувачів
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, View, FormView
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView, PasswordResetView
from django.contrib import messages
from .models import CustomUser
from .forms import WholesaleRegistrationForm, CustomLoginForm, CustomPasswordResetForm
from .utils import send_verification_email
import logging

logger = logging.getLogger(__name__)


class WholesaleRegisterView(CreateView):
    """Реєстрація тільки для оптових клієнтів"""
    
    model = CustomUser
    form_class = WholesaleRegistrationForm
    template_name = 'users/register.html'
    
    def form_valid(self, form):
        try:
            # Зберігаємо користувача (is_active=False)
            user = form.save()
            logger.info(f"📝 New user registered: {user.email} (username: {user.username})")
            
            # Надсилаємо лист з підтвердженням
            if send_verification_email(user, self.request):
                logger.info(f"✅ Verification email sent successfully to: {user.email}")
                messages.success(
                    self.request, 
                    'Ви успішно зареєструвалися! Перевірте вашу пошту для підтвердження email.'
                )
            else:
                logger.error(f"❌ Failed to send verification email to: {user.email}")
                messages.warning(
                    self.request,
                    'Реєстрація успішна, але виникла помилка при надсиланні листа. Зверніться до підтримки.'
                )
            
            return redirect('users:registration_pending')
            
        except Exception as e:
            logger.error(f"❌ Registration error: {str(e)}", exc_info=True)
            messages.error(
                self.request,
                f'Виникла помилка при реєстрації: {str(e)}. Спробуйте ще раз або зверніться до підтримки.'
            )
            return super().form_invalid(form)
    
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
    
    authentication_form = CustomLoginForm
    template_name = 'users/login.html'
    
    def form_invalid(self, form):
        username = form.data.get('username', '')
        
        if username:
            # Перевіряємо чи існує користувач з таким email/username
            try:
                user = CustomUser.objects.filter(email=username).first() or \
                       CustomUser.objects.filter(username=username).first()
                
                if not user:
                    messages.error(
                        self.request,
                        'Користувача з такими даними не зареєстровано. Будь ласка, зареєструйтеся.'
                    )
                elif not user.is_active:
                    messages.error(
                        self.request,
                        'Ваш акаунт ще не активовано. Будь ласка, перевірте вашу пошту та підтвердіть email.'
                    )
                else:
                    messages.error(
                        self.request,
                        'Невірний пароль. Перевірте правильність введення паролю.'
                    )
            except Exception:
                messages.error(self.request, 'Невірні дані для входу.')
        else:
            messages.error(self.request, 'Будь ласка, введіть дані для входу.')
        
        return super().form_invalid(form)


class CustomPasswordResetView(PasswordResetView):
    """Кастомний view для відновлення паролю з детальним логуванням"""
    
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = '/users/password/reset/done/'
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        logger.info(f"🔐 Password reset requested for email: {email}")
        
        # Перевіряємо чи існує користувач
        users = CustomUser.objects.filter(email__iexact=email, is_active=True)
        if users.exists():
            logger.info(f"✅ User found: {users.first().username}")
        else:
            logger.warning(f"⚠️ No active user found with email: {email}")
        
        try:
            response = super().form_valid(form)
            logger.info(f"📧 Password reset email should be sent to: {email}")
            return response
        except Exception as e:
            logger.error(f"❌ Error in password reset: {str(e)}", exc_info=True)
            messages.error(
                self.request,
                f'Виникла помилка при відправці email: {str(e)}'
            )
            return self.form_invalid(form)
