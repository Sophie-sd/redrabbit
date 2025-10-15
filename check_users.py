#!/usr/bin/env python3
"""
Скрипт для перевірки існуючих користувачів
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings.production')
django.setup()

from apps.users.models import CustomUser

print("\n" + "="*60)
print("📋 СПИСОК ВСІХ КОРИСТУВАЧІВ В БАЗІ ДАНИХ")
print("="*60 + "\n")

users = CustomUser.objects.all().order_by('-is_superuser', '-is_staff', 'username')

if not users.exists():
    print("⚠️ В базі даних немає жодного користувача!")
else:
    for user in users:
        print(f"👤 Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Phone: {getattr(user, 'phone', 'N/A')}")
        print(f"   Superuser: {'✅' if user.is_superuser else '❌'}")
        print(f"   Staff: {'✅' if user.is_staff else '❌'}")
        print(f"   Active: {'✅' if user.is_active else '❌'}")
        print(f"   Email Verified: {'✅' if getattr(user, 'email_verified', False) else '❌'}")
        print(f"   Date Joined: {user.date_joined}")
        print(f"   Last Login: {user.last_login or 'Ніколи'}")
        print("-" * 60)

print("\n" + "="*60)
print(f"📊 ВСЬОГО КОРИСТУВАЧІВ: {users.count()}")
print(f"👑 Суперюзерів: {users.filter(is_superuser=True).count()}")
print(f"👥 Активних: {users.filter(is_active=True).count()}")
print("="*60 + "\n")

# Додаткова інформація для адмінів
superusers = users.filter(is_superuser=True, is_staff=True)
if superusers.exists():
    print("🔐 ДАНІ ДЛЯ ВХОДУ В ADMIN:")
    for su in superusers:
        print(f"   Username: {su.username}")
        print(f"   Email: {su.email}")
        print(f"   🌐 URL: https://your-app-name.onrender.com/admin/")
        print("-" * 60)
else:
    print("❌ НЕМАЄ ЖОДНОГО СУПЕРЮЗЕРА! Створіть через:")
    print("   python create_superuser.py")

