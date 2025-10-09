# 👆 Покрокова інструкція для Render (з екранними вказівками)

## 🎯 МЕТА
Задеплоїти BeautyShop на Render.com з повним функціоналом особистого кабінету та відправкою email.

---

## 📍 КРОК 1: ПІДГОТОВКА (5 хвилин)

### Що вам знадобиться:

✅ **Акаунт Render:**
1. Відкрийте: https://render.com
2. Клікніть "Get Started" (вгорі справа)
3. Зареєструйтеся через GitHub (рекомендовано)

✅ **Gmail дані (вже готові):**
- Email: `beautyshop.supp@gmail.com`
- App Password: `ymycifcxvdrtvrvx`

✅ **Пароль для адміна (придумайте):**
- Наприклад: `BeautyAdmin2024!`
- Запишіть його, він знадобиться!

---

## 📍 КРОК 2: СТВОРЕННЯ POSTGRESQL DATABASE (3 хвилини)

### 2.1. На Render Dashboard

1. **Клікніть синю кнопку "New +" (вгорі справа)**
2. **Оберіть "PostgreSQL"**

### 2.2. Заповніть форму:

```
┌─────────────────────────────────────┐
│ Name: beautyshop-db                 │ ← Назва бази даних
├─────────────────────────────────────┤
│ Database: beautyshop                │ ← Ім'я бази
├─────────────────────────────────────┤
│ User: beautyshop_user               │ ← Користувач
├─────────────────────────────────────┤
│ Region: Frankfurt (EU Central) ★    │ ← ВАЖЛИВО: EU регіон!
├─────────────────────────────────────┤
│ PostgreSQL Version: 15              │ ← Версія
├─────────────────────────────────────┤
│ Plan: Free                          │ ← Безкоштовний план
└─────────────────────────────────────┘
```

### 2.3. Клікніть "Create Database"

⏳ Зачекайте 1-2 хвилини поки створюється...

### 2.4. Скопіюйте Internal Database URL:

```
┌──────────────────────────────────────────────────────┐
│ 📋 Internal Database URL                             │
│ postgresql://beautyshop_user:pass@...               │
│ [Copy] ← КЛІКНІТЬ ТУТ                                │
└──────────────────────────────────────────────────────┘
```

**⚠️ ЗБЕРЕЖІТЬ ЦЕЙ URL!** Він знадобиться в кроці 4.

---

## 📍 КРОК 3: СТВОРЕННЯ WEB SERVICE (5 хвилин)

### 3.1. Поверніться на Dashboard

1. **Клікніть "New +" знову**
2. **Оберіть "Web Service"**

### 3.2. Підключіть GitHub:

```
┌──────────────────────────────────────────────────────┐
│ Connect a repository                                 │
│                                                      │
│ [Configure Account] ← Якщо перший раз               │
│                                                      │
│ 🔍 Search: BeautyShop                               │
│ ✓ Sophie-sd/BeautyShop          [Connect]          │
└──────────────────────────────────────────────────────┘
```

### 3.3. Основні налаштування:

```
┌─────────────────────────────────────┐
│ Name: beautyshop-django             │ ← Назва сервісу
├─────────────────────────────────────┤
│ Region: Frankfurt (EU Central) ★    │ ← ТОЙ САМИЙ що БД!
├─────────────────────────────────────┤
│ Branch: main                        │ ← Гілка Git
├─────────────────────────────────────┤
│ Root Directory: (порожнє)           │ ← Залиште порожнім
├─────────────────────────────────────┤
│ Runtime: Python 3                   │ ← Автоматично
├─────────────────────────────────────┤
│ Build Command:                      │
│ chmod +x build.sh && ./build.sh     │ ← Скопіюйте точно!
├─────────────────────────────────────┤
│ Start Command:                      │
│ gunicorn beautyshop.wsgi:application│
│ --bind 0.0.0.0:$PORT --workers 4    │ ← Скопіюйте точно!
│ --timeout 120                       │
├─────────────────────────────────────┤
│ Plan: Free                          │ ← Безкоштовний
└─────────────────────────────────────┘
```

### 3.4. НЕ КЛІКАЙТЕ "Create Web Service" ЩЕ!

**Спочатку додамо змінні середовища ↓**

---

## 📍 КРОК 4: ДОДАВАННЯ ЗМІННИХ СЕРЕДОВИЩА (15 хвилин)

### 4.1. Розгорніть "Advanced" (внизу форми)

### 4.2. Знайдіть секцію "Environment Variables"

### 4.3. Клікніть "Add Environment Variable" 16 разів

**Додавайте по одній змінній:**

---

### 📧 БЛОК 1: Django Налаштування

#### Змінна 1:
```
Key:   DJANGO_SETTINGS_MODULE
Value: beautyshop.settings.production
```

#### Змінна 2:
```
Key:   DEBUG
Value: False
```

---

### 🌐 БЛОК 2: Хости та безпека

#### Змінна 3:
```
Key:   ALLOWED_HOSTS
Value: beautyshop-django.onrender.com,beautyshop-django-*.onrender.com
```

#### Змінна 4:
```
Key:   CSRF_TRUSTED_ORIGINS
Value: https://beautyshop-django.onrender.com
```

#### Змінна 5:
```
Key:   SITE_URL
Value: https://beautyshop-django.onrender.com
```

---

### 💾 БЛОК 3: База даних

#### Змінна 6:
```
Key:   DATABASE_URL
Value: [ВСТАВТЕ Internal Database URL з кроку 2.4]
```

**⚠️ Має виглядати приблизно так:**
```
postgresql://beautyshop_user:xxxxx@dpg-xxxxx.frankfurt-postgres.render.com/beautyshop
```

---

### 📧 БЛОК 4: Email (Gmail)

#### Змінна 7:
```
Key:   EMAIL_BACKEND
Value: django.core.mail.backends.smtp.EmailBackend
```

#### Змінна 8:
```
Key:   EMAIL_HOST
Value: smtp.gmail.com
```

#### Змінна 9:
```
Key:   EMAIL_PORT
Value: 587
```

#### Змінна 10:
```
Key:   EMAIL_USE_TLS
Value: True
```

#### Змінна 11:
```
Key:   EMAIL_USE_SSL
Value: False
```

#### Змінна 12:
```
Key:   EMAIL_HOST_USER
Value: beautyshop.supp@gmail.com
```

#### Змінна 13:
```
Key:   EMAIL_HOST_PASSWORD
Value: ymycifcxvdrtvrvx
```

**⚠️ БЕЗ ПРОБІЛІВ!** Копіюйте точно: `ymycifcxvdrtvrvx`

#### Змінна 14:
```
Key:   DEFAULT_FROM_EMAIL
Value: Beauty Shop <beautyshop.supp@gmail.com>
```

---

### 👤 БЛОК 5: Адміністратор

#### Змінна 15:
```
Key:   ADMIN_EMAIL
Value: admin@beautyshop.ua
```

#### Змінна 16:
```
Key:   ADMIN_PASSWORD
Value: BeautyAdmin2024!
```

**⚠️ ЗМІНІТЬ на свій сильний пароль!**
- Мінімум 8 символів
- Великі та малі літери
- Цифри та спецсимволи

---

### 4.4. Перевірте що всі 16 змінних додано

```
✅ DJANGO_SETTINGS_MODULE
✅ DEBUG
✅ ALLOWED_HOSTS
✅ CSRF_TRUSTED_ORIGINS
✅ SITE_URL
✅ DATABASE_URL
✅ EMAIL_BACKEND
✅ EMAIL_HOST
✅ EMAIL_PORT
✅ EMAIL_USE_TLS
✅ EMAIL_USE_SSL
✅ EMAIL_HOST_USER
✅ EMAIL_HOST_PASSWORD
✅ DEFAULT_FROM_EMAIL
✅ ADMIN_EMAIL
✅ ADMIN_PASSWORD
```

---

## 📍 КРОК 5: ЗАПУСК ДЕПЛОЮ (10-15 хвилин)

### 5.1. Тепер клікніть "Create Web Service"

⏳ Render почне деплой...

### 5.2. Спостерігайте за логами:

```
┌──────────────────────────────────────────────┐
│ Logs                                         │
├──────────────────────────────────────────────┤
│ ==> Cloning from GitHub...                   │
│ ✅ Clone successful                          │
│                                              │
│ ==> Installing dependencies...              │
│ ✅ Collecting Django==4.2.x...               │
│                                              │
│ ==> Running build.sh...                      │
│ ✅ Collecting static files...                │
│ ✅ 156 static files copied                   │
│                                              │
│ ==> Running migrations...                    │
│ ✅ Applying migrations...                    │
│ ✅ Operations to perform: 15 migrations      │
│                                              │
│ ==> Creating superuser...                    │
│ ✅ Superuser created: admin@beautyshop.ua    │
│                                              │
│ ==> Starting server...                       │
│ ✅ Listening at: http://0.0.0.0:10000        │
│ ✅ Booting worker with pid: 42               │
│                                              │
│ 🎉 Your service is live at...               │
│ https://beautyshop-django.onrender.com      │
└──────────────────────────────────────────────┘
```

### 5.3. Чекайте на статус "Live" (зелений)

```
Status: ● Live    ← Має бути зелений кружок
```

---

## 📍 КРОК 6: ПЕРЕВІРКА (10 хвилин)

### 6.1. Головна сторінка

**Відкрийте:**
```
https://beautyshop-django.onrender.com/
```

**Має показатися:**
✅ Головна сторінка сайту
✅ Товари
✅ Меню навігації
✅ Footer

**Якщо бачите помилку:**
❌ Перевірте логи: Web Service → Logs

---

### 6.2. Адмін панель

**Відкрийте:**
```
https://beautyshop-django.onrender.com/admin/
```

**Введіть:**
- Username або Email: `admin@beautyshop.ua`
- Password: `ваш ADMIN_PASSWORD з кроку 4`

**Має:**
✅ Успішно увійти
✅ Показати Django Admin інтерфейс
✅ Бачити користувачів, товари, категорії

---

### 6.3. Реєстрація користувача

**Відкрийте:**
```
https://beautyshop-django.onrender.com/users/register/
```

**Зареєструйте тестового користувача:**
1. Заповніть всі поля
2. Телефон: `+380991234567`
3. Email: `test@example.com`
4. Натисніть "Зареєструватися"

**Має:**
✅ Показати "Перевірте пошту"
✅ Email надіслати на `beautyshop.supp@gmail.com`

---

### 6.4. Перевірка Email

**Зайдіть в пошту:**
```
beautyshop.supp@gmail.com
```

**Має бути лист:**
```
┌──────────────────────────────────────────────┐
│ 📧 Підтвердження email - BeautyShop         │
│ Від: Beauty Shop <beautyshop.supp@gmail.com>│
│                                              │
│ Вітаємо!                                     │
│ Дякуємо за реєстрацію...                    │
│                                              │
│ [Підтвердити email] ← Клікніть              │
└──────────────────────────────────────────────┘
```

**Клікніть посилання:**
✅ Має активувати користувача
✅ Автоматично увійти
✅ Перенаправити в особистий кабінет

---

### 6.5. Відновлення паролю

**Відкрийте:**
```
https://beautyshop-django.onrender.com/users/password/reset/
```

**Введіть:** `test@example.com`

**Має:**
✅ Показати "Лист надіслано"
✅ Email прийти на `beautyshop.supp@gmail.com`
✅ Посилання для зміни паролю працює

---

### 6.6. Оптові ціни

**Увійдіть як admin:**
```
https://beautyshop-django.onrender.com/users/login/
Email: admin@beautyshop.ua
Password: ваш ADMIN_PASSWORD
```

**Відкрийте будь-який товар:**

**Має показувати:**
```
Ціна: 250 грн
Ціна від 3 шт: 220 грн
Оптова ціна: 200 грн ← Тільки для авторизованих!
```

**Вийдіть та перевірте:**
- Оптова ціна має зникнути
- Показуються тільки: Ціна та Ціна від 3 шт

---

## ✅ КРОК 7: ВСЕ ПРАЦЮЄ!

### Якщо всі тести пройшли успішно:

```
✅ Головна сторінка відкривається
✅ Адмін панель працює
✅ Реєстрація працює
✅ Email надсилається
✅ Верифікація email працює
✅ Відновлення паролю працює
✅ Оптові ціни показуються тільки авторизованим
✅ Static files завантажуються
✅ HTTPS працює
✅ База даних працює
```

### 🎉 ВАШ САЙТ ОНЛАЙН!

**URL:**
```
https://beautyshop-django.onrender.com
```

---

## ❌ ЩО РОБИТИ ЯКЩО ЩОСЬ НЕ ПРАЦЮЄ?

### Проблема 1: Email не надсилається

**Перевірте в Environment Variables:**
1. `EMAIL_HOST_PASSWORD` = `ymycifcxvdrtvrvx` (без пробілів!)
2. `EMAIL_HOST_USER` = `beautyshop.supp@gmail.com`
3. `EMAIL_PORT` = `587`
4. `EMAIL_USE_TLS` = `True`

**Тест в Shell:**
1. Web Service → Shell (вгорі справа)
2. Введіть:
```python
from django.core.mail import send_mail
result = send_mail('Test', 'Test', 'beautyshop.supp@gmail.com', ['beautyshop.supp@gmail.com'])
print(f'Result: {result}')
```
3. Має вивести: `Result: 1`

---

### Проблема 2: 500 Error

**Перевірте логи:**
1. Web Service → Logs
2. Шукайте червоні помилки
3. Типові причини:
   - `ALLOWED_HOSTS` - неправильний домен
   - `DATABASE_URL` - немає з'єднання з БД
   - `SECRET_KEY` - не встановлено

**Виправлення:**
- Перевірте всі 16 змінних
- Перезапустіть: Manual Deploy

---

### Проблема 3: Не входить в Admin

**Перевірте:**
1. Email: `admin@beautyshop.ua` (точно так!)
2. Password: ваш `ADMIN_PASSWORD`
3. В логах: "Superuser created"

**Якщо забули пароль:**
1. Shell → Введіть:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.get(email='admin@beautyshop.ua')
admin.set_password('НовийПароль123!')
admin.save()
print('Password changed!')
```

---

### Проблема 4: Static files не завантажуються

**Перевірте:**
1. Логи: `collectstatic` виконався?
2. Має бути: `X static files copied`
3. Якщо ні - Manual Deploy

**Тимчасове вирішення:**
- Ctrl+Shift+R (очистити кеш браузера)

---

## 📞 ПІДТРИМКА

### Якщо нічого не допомагає:

**1. Перевірте детальну інструкцію:**
```
RENDER_DEPLOYMENT_GUIDE.md
```

**2. Перевірте швидкий старт:**
```
RENDER_QUICK_START.md
```

**3. Render Community:**
```
https://community.render.com
```

**4. Email:**
```
beautyshop.supp@gmail.com
```

---

## 🎓 КОРИСНІ КОМАНДИ

### В Render Shell:

**Створити тестового користувача:**
```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_user(
    username='testuser',
    email='test@test.com',
    password='Test1234!',
    phone='+380991111111',
    first_name='Test',
    last_name='User',
    is_active=True
)
print(f'User created: {user.email}')
```

**Перевірити email налаштування:**
```python
from django.conf import settings
print(f'EMAIL_HOST: {settings.EMAIL_HOST}')
print(f'EMAIL_PORT: {settings.EMAIL_PORT}')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
```

**Список всіх користувачів:**
```python
from django.contrib.auth import get_user_model
User = get_user_model()
for user in User.objects.all():
    print(f'{user.email} - Active: {user.is_active}')
```

---

**Успіхів! 🚀**

Якщо всі кроки виконано правильно, ваш сайт працює на production з повним функціоналом!

