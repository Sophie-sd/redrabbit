#!/usr/bin/env bash
# Build script для Render.com

# Встановлюємо залежності
pip install -r requirements.txt

# Збираємо статичні файли
python manage.py collectstatic --no-input

# Застосовуємо міграції
python manage.py migrate --no-input

# Створюємо категорії (безпечно)
python manage.py create_categories

# Створюємо суперюзера якщо не існує
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
admin_password = os.getenv('ADMIN_PASSWORD', 'ChangeMe123!')
if not User.objects.filter(email=admin_email).exists():
    user = User.objects.create_superuser(
        username='admin',
        email=admin_email,
        password=admin_password,
        phone='+380000000000',
        first_name='Admin',
        last_name='User'
    )
    print(f'✅ Superuser created: {admin_email}')
else:
    print(f'⚠️ Superuser already exists: {admin_email}')
"

echo "✅ Build completed successfully!"