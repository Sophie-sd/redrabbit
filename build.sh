#!/usr/bin/env bash
set -o errexit

echo "📦 Встановлення залежностей..."
pip install -r requirements.txt

echo "🗂️  Збір статичних файлів..."
python manage.py collectstatic --no-input

echo "🔄 Застосування міграцій..."
python manage.py migrate products 0027 --fake --no-input 2>/dev/null || true
python manage.py migrate products 0028 --fake --no-input 2>/dev/null || true
python manage.py migrate --no-input

echo "📦 Налаштування БД..."
python production_setup.py || echo "⚠️  Імпорт завершено з попередженнями"

echo "📝 Оновлення відгуків..."
python manage.py create_reviews || echo "⚠️  Відгуки не оновлено"

echo "✅ Build completed!"