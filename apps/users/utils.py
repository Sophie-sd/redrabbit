"""
Утиліти для роботи з користувачами
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


def send_verification_email(user, request):
    """
    Надсилає лист з підтвердженням email користувачу
    """
    # Генеруємо токен
    token = user.generate_email_verification_token()
    
    # Будуємо URL для верифікації
    verification_url = request.build_absolute_uri(
        reverse('users:verify_email', kwargs={'token': token})
    )
    
    # Контекст для шаблону
    context = {
        'user': user,
        'verification_url': verification_url,
    }
    
    # Рендеримо HTML версію
    html_message = render_to_string('emails/email_verification.html', context)
    plain_message = strip_tags(html_message)
    
    # Надсилаємо лист
    try:
        send_mail(
            subject='Підтвердження email - BeautyShop',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user, request, token, uidb64):
    """
    Надсилає лист з посиланням для відновлення паролю
    """
    # Будуємо URL для відновлення
    reset_url = request.build_absolute_uri(
        reverse('users:password_reset_confirm', kwargs={
            'uidb64': uidb64,
            'token': token
        })
    )
    
    # Контекст для шаблону
    context = {
        'user': user,
        'reset_url': reset_url,
    }
    
    # Рендеримо HTML версію
    html_message = render_to_string('emails/password_reset.html', context)
    plain_message = strip_tags(html_message)
    
    # Надсилаємо лист
    try:
        send_mail(
            subject='Відновлення паролю - BeautyShop',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False

