"""
Custom authentication backend для входу через email
"""
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Дозволяє користувачам входити через email або username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # Спробуємо знайти користувача за email
        try:
            user = CustomUser.objects.get(email=username)
        except CustomUser.DoesNotExist:
            # Якщо не email, спробуємо username
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                return None
        
        # Перевіряємо пароль
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None

