"""
Middleware для перевірки валідності користувача в сесії.
"""
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser


class ValidateUserMiddleware:
    """
    Middleware для перевірки, чи існує користувач в базі даних.
    Якщо користувач видалений, але сесія все ще активна - виконується logout.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Перевіряємо, чи користувач залогінений
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Спробуємо отримати користувача з бази даних
                # Це викличе DoesNotExist, якщо користувача видалено
                if request.user.pk:
                    # Перевіряємо, чи користувач існує в БД
                    from apps.users.models import CustomUser
                    CustomUser.objects.get(pk=request.user.pk)
            except Exception:
                # Користувача не існує в БД - виходимо з системи
                logout(request)
                # Встановлюємо AnonymousUser
                request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response

