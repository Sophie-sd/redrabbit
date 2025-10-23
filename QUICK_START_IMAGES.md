# ⚡ ШВИДКИЙ ЗАПУСК КАРТИНОК

## 🎯 Мета
Швидко додати картинки до 8,348 товарів без зображень і налаштувати автоматичне оновлення.

## 🚀 Крок за кроком

### 1️⃣ ТЕСТУВАННЯ (2 хвилини)
```bash
# Протестувати на 10 товарах
./test_images_download.py
```

### 2️⃣ МАСОВЕ ЗАВАНТАЖЕННЯ (2-4 години)
```bash
# Завантажити всі картинки
./download_all_images.py
```

### 3️⃣ АВТОМАТИЧНЕ ОНОВЛЕННЯ (1 хвилина)
```bash
# Налаштувати cron jobs
./setup_sync_cron.sh
```

## 📊 Перевірка результату

```bash
# Подивитись скільки товарів отримали картинки
python3 manage.py shell -c "
from apps.products.models import Product
with_images = Product.objects.filter(images__isnull=False).distinct().count()
without_images = Product.objects.filter(images__isnull=True).count()
print(f'✅ З картинками: {with_images}')
print(f'❌ Без картинок: {without_images}')
print(f'📈 Прогрес: {round(with_images/(with_images+without_images)*100, 1)}%')
"
```

## ⚠️ УВАГА
- **Інтернет**: потрібне стабільне з'єднання
- **Час**: перше завантаження ~2-4 години  
- **Диск**: потрібно ~400MB-1.6GB вільного місця
- **Сервер**: буде навантаження на smtm.com.ua

## 🆘 У разі проблем

### Якщо завантаження зупинилось:
```bash
# Перезапустити з більшою затримкою
python3 manage.py bulk_download_images --delay 0.5 --max-retries 5
```

### Якщо потрібно швидше:
```bash
# Прискорити (ризик помилок)
python3 manage.py bulk_download_images --delay 0 --batch-size 200
```

### Перевірка логів:
```bash
# Дивитись прогрес в реальному часі
tail -f /tmp/intshop_images.log
```

## ✅ Після завершення

Ваші товари будуть автоматично оновлюватись:
- **Кожні 2 години**: нові ціни та картинки
- **Щодня о 3:00**: пошук товарів без картинок  
- **Щодня о 8:00**: імпорт нових товарів

**Готово! 🎉**
