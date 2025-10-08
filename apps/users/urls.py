"""
URLs для користувачів
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Реєстрація
    path('register/', views.WholesaleRegisterView.as_view(), name='register'),
    path('registration-pending/', views.RegistrationPendingView.as_view(), name='registration_pending'),
    path('verify-email/<str:token>/', views.EmailVerificationView.as_view(), name='verify_email'),
    
    # Вхід/вихід
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    
    # Особистий кабінет
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('orders/', views.UserOrdersView.as_view(), name='orders'),
    
    # Відновлення паролю
    path('password/reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password/reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password/reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]
