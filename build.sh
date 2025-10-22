#!/usr/bin/env bash
set -o errexit

echo "📦 Встановлення залежностей..."
pip install -r requirements.txt

echo "🗂️  Збір статичних файлів..."
python manage.py collectstatic --no-input

echo "🔄 Застосування міграцій..."
python manage.py migrate --no-input

echo "📦 Налаштування БД..."
python production_setup.py || echo "⚠️  Імпорт завершено з попередженнями"

echo "✅ Build completed!"