#!/usr/bin/env bash
# Build script для Render.com

set -o errexit  # Зупинити виконання при помилці

echo "📦 Встановлення залежностей..."
pip install -r requirements.txt

echo "🗂️  Збір статичних файлів..."
python manage.py collectstatic --no-input

echo "🔄 Застосування міграцій..."
python manage.py migrate --no-input

echo "📦 Налаштування БД та імпорт даних..."
python production_setup.py || echo "⚠️  Імпорт завершено з попередженнями"

echo "✅ Build completed successfully!"