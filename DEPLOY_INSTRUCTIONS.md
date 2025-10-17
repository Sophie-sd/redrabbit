# Інструкція з деплою на Render.com

## Що змінено

### ✅ Виправлено в `render.yaml`:
- Спрощено buildCommand — тепер використовується `build.sh`
- Видалено потрійне дублювання створення суперюзера
- Це усуває конфлікти та помилки з імпортом моделей

### ✅ Виправлено в `build.sh`:
- Додано `set -o errexit` для зупинки при помилках
- Видалено створення суперюзера з build-процесу (буде створено вручну після деплою)
- Додано інформативні повідомлення

## Кроки після деплою

### 1. Після успішного деплою створіть суперюзера:

```bash
# В Render Shell виконайте:
python manage.py reset_admin
```

Або вручну через Django Shell:
```bash
python manage.py shell
```

```python
from apps.users.models import CustomUser
import os

User = CustomUser
username = os.getenv('ADMIN_USERNAME', 'admin')
email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
password = 'ChangeMe123!'
phone = '+380000000000'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        phone=phone,
        first_name='Admin',
        last_name='User'
    )
    print(f'✅ Superuser created: {username}')
else:
    print(f'⚠️ User already exists')
```

### 2. Перевірте що міграції застосовані:

```bash
python manage.py showmigrations
```

Переконайтесь що всі міграції позначені `[X]`, особливо:
- `products.0011_add_review_brand_video` — додає поле `video_url`

### 3. Якщо міграції не застосовані:

```bash
python manage.py migrate --no-input
```

### 4. Перевірте сайт:

Відкрийте у браузері:
- Головну сторінку: `https://your-app.onrender.com/`
- Адмін-панель: `https://your-app.onrender.com/admin/`

## Дані для входу

- **Username:** admin (або значення з `ADMIN_USERNAME`)
- **Password:** ChangeMe123! (або значення з `ADMIN_PASSWORD`)
- **Email:** admin@example.com (або значення з `ADMIN_EMAIL`)

⚠️ **ОБОВ'ЯЗКОВО ЗМІНІТЬ ПАРОЛЬ** після першого входу!

## Environment Variables в Render

Переконайтесь що налаштовані:
- `DATABASE_URL` — автоматично з Render DB
- `SECRET_KEY` — згенеровано Render
- `DEBUG` — False
- `DJANGO_SETTINGS_MODULE` — shop.settings.production
- `ALLOWED_HOSTS` — ваш домен Render
- `ADMIN_USERNAME` — admin (опціонально)
- `ADMIN_EMAIL` — ваш email (опціонально)
- `ADMIN_PASSWORD` — безпечний пароль (опціонально)
- `CLOUDINARY_*` — для медіа файлів (якщо використовуєте)

## Troubleshooting

### Помилка: "column products_product.video_url does not exist"

**Причина:** Міграція 0011 не застосована.

**Рішення:**
```bash
python manage.py migrate products 0011 --fake
python manage.py migrate
```

### Build падає з помилкою

**Перевірте логи Render:**
1. Відкрийте Dashboard → Events
2. Шукайте червоні повідомлення
3. Перевірте чи встановились всі залежності з `requirements.txt`

### Сайт не відкривається (502/504)

**Можливі причини:**
1. База даних не доступна — перевірте `DATABASE_URL`
2. Не застосовані міграції — запустіть `python manage.py migrate`
3. Не створені статичні файли — перевірте що `collectstatic` спрацював

## Корисні команди для Render Shell

```bash
# Перевірити з'єднання з БД
python manage.py dbshell

# Список всіх користувачів
python manage.py shell -c "from apps.users.models import CustomUser; print(CustomUser.objects.all().values('username', 'email', 'is_superuser'))"

# Скинути пароль існуючого адміна
python manage.py reset_admin

# Створити категорії
python manage.py create_categories

# Перевірити налаштування
python manage.py check --deploy
```

