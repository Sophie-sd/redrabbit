#!/usr/bin/env python3
"""
Скрипт для автоматичного створення суперюзера на production (Render)
"""

import os
import django

def create_superuser():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beautyshop.settings.production')
    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Дані для суперюзера
    username = 'beautyshop'
    email = 'admin@beautyshop.ua'
    password = '123456'

    # Перевіряємо чи вже існує
    if User.objects.filter(username=username).exists():
        print(f'✅ Користувач {username} вже існує')
        user = User.objects.get(username=username)
        # Оновлюємо пароль на всякий випадок
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        print(f'🔄 Пароль та права оновлено')
    else:
        # Створюємо нового
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f'✅ Створено нового суперюзера: {username}')

    print(f'👤 Username: {username}')
    print(f'🔑 Password: {password}')
    print(f'📧 Email: {email}')
    print(f'🚀 Готово до роботи!')

if __name__ == '__main__':
    create_superuser()
