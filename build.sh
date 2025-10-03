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
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@beautyshop.ua', '123456')
    print('Superuser created')
else:
    print('Superuser already exists')
"

echo "✅ Build completed successfully!"