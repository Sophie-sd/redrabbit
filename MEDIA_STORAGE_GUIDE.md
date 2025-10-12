# 📦 Керівництво з налаштування зберігання Media файлів

## 🚨 Проблема на Render.com

**Render.com використовує ephemeral filesystem:**
- ❌ Всі завантажені файли зникають при редеплої
- ❌ При перезапуску сервера файли втрачаються
- ❌ Whitenoise НЕ обслуговує media файли (тільки static)

**Результат:**
- Банери завантажуються в адмінці ✓
- Зберігаються в БД ✓
- Але файли зникають після перезапуску ✗

---

## ✅ Рішення: Cloudinary (безкоштовний план)

**Cloudinary** — це CDN для зображень з безкоштовним планом:
- 25 GB зберігання
- 25 GB bandwidth
- Автоматична оптимізація зображень
- Responsive images
- CDN по всьому світу

---

## 🔧 Налаштування Cloudinary

### Крок 1: Реєстрація на Cloudinary

1. Перейти на: https://cloudinary.com/users/register_free
2. Зареєструватися (безкоштовно)
3. Після реєстрації отримаєте:
   ```
   Cloud name: dxxxxx
   API Key: 123456789012345
   API Secret: abcdefghijklmnopqrstuvwxyz
   ```

---

### Крок 2: Встановити пакети

Додати в `requirements.txt`:
```txt
cloudinary==1.36.0
django-cloudinary-storage==0.3.0
```

Встановити локально:
```bash
pip install cloudinary django-cloudinary-storage
```

---

### Крок 3: Налаштувати Django

#### **settings/base.py:**

```python
# Додати в INSTALLED_APPS (перед django.contrib.staticfiles!)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',  # ← ДОДАТИ СЮДИ
    'django.contrib.staticfiles',
    'cloudinary',  # ← І СЮДИ
    # ... інші додатки
]
```

#### **settings/production.py:**

```python
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Cloudinary configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Django 4.2+ STORAGES
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Media files через Cloudinary
MEDIA_URL = '/media/'  # Cloudinary перевизначить це
```

---

### Крок 4: Додати змінні оточення на Render

В Render Dashboard → Environment Variables:

```
CLOUDINARY_CLOUD_NAME=dxxxxx
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz
```

---

### Крок 5: Оновити render.yaml

```yaml
envVars:
  # ... існуючі змінні
  - key: CLOUDINARY_CLOUD_NAME
    sync: false  # Додаємо вручну через dashboard
  - key: CLOUDINARY_API_KEY
    sync: false
  - key: CLOUDINARY_API_SECRET
    sync: false
```

---

## 🎯 Як це працюватиме

### Завантаження:
```python
# Адмін завантажує файл
banner.desktop_image = uploaded_file
banner.save()

↓

# Django відправляє на Cloudinary
POST https://api.cloudinary.com/v1_1/dxxxxx/image/upload

↓

# Cloudinary зберігає та повертає URL
https://res.cloudinary.com/dxxxxx/image/upload/v123/banners/desktop/image.jpg
```

### Відображення:
```html
<!-- В шаблоні -->
<img src="{{ banner.desktop_image.url }}" alt="{{ banner.alt_text }}">

↓

<!-- Рендериться як -->
<img src="https://res.cloudinary.com/dxxxxx/image/upload/v123/banners/desktop/image.jpg" alt="...">
```

---

## 🔄 Міграція існуючих зображень

Якщо вже є завантажені зображення локально:

```python
# create_migration_script.py
import cloudinary.uploader
from apps.core.models import Banner

for banner in Banner.objects.all():
    if banner.desktop_image:
        # Завантажити на Cloudinary
        result = cloudinary.uploader.upload(
            banner.desktop_image.path,
            folder='banners/desktop'
        )
        banner.desktop_image = result['public_id']
        banner.save()
```

---

## ✅ Переваги Cloudinary

| Функція | Опис |
|---------|------|
| **CDN** | Швидка доставка з найближчого сервера |
| **Оптимізація** | Автоматичне стиснення без втрати якості |
| **Responsive** | Автоматичне масштабування під різні екрани |
| **Backup** | Файли не втрачаються при редеплої |
| **Transform** | Обрізка, ресайз на льоту через URL |
| **Free tier** | 25 GB зберігання + 25 GB bandwidth |

---

## 🆚 Альтернативи

### AWS S3 (популярний, але платний)
```bash
pip install boto3 django-storages
```
```python
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'beautyshop-media'
```

### Render Disks (платний - $1/GB/місяць)
```yaml
services:
  - type: web
    disk:
      name: media-disk
      mountPath: /opt/render/project/src/media
      sizeGB: 1
```

### DigitalOcean Spaces (схожий на S3)
```bash
pip install boto3 django-storages
```
```python
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_ENDPOINT_URL = 'https://nyc3.digitaloceanspaces.com'
```

---

## 📝 Чеклист впровадження

- [ ] Зареєструватися на Cloudinary
- [ ] Отримати Cloud name, API Key, API Secret
- [ ] Додати пакети в requirements.txt
- [ ] Оновити settings/base.py (INSTALLED_APPS)
- [ ] Оновити settings/production.py (STORAGES)
- [ ] Додати env vars на Render Dashboard
- [ ] Редеплоїти на Render
- [ ] Завантажити тестовий банер
- [ ] Перевірити що зображення відображається
- [ ] Перезапустити сервер - зображення має залишитися

---

## 🔍 Діагностика проблем

### Зображення не завантажується:
```python
# Перевірити в Django shell
from django.conf import settings
print(settings.STORAGES)
print(settings.CLOUDINARY_STORAGE)
```

### Зображення завантажилося, але не відображається:
```python
# Перевірити URL
from apps.core.models import Banner
banner = Banner.objects.first()
print(banner.desktop_image.url)
# Має бути: https://res.cloudinary.com/...
```

### Помилка авторизації:
- Перевірити правильність CLOUDINARY_API_KEY та API_SECRET
- Перевірити що змінні додані на Render Dashboard
- Перезапустити сервер після додавання змінних

---

## 💰 Вартість

**Cloudinary Free Plan:**
- Зберігання: 25 GB
- Bandwidth: 25 GB/місяць
- Requests: 25,000/місяць
- Transformations: 25 credits/місяць

**Для Beauty Shop це достатньо:**
- ~100 банерів × 500 KB = 50 MB
- ~1000 товарів × 200 KB = 200 MB
- Всього: ~250 MB (1% від ліміту)

---

**Рекомендація:** Використовуйте Cloudinary для production на Render.com!

**Документація:** https://cloudinary.com/documentation/django_integration

