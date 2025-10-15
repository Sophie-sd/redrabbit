# 🛒 Django E-commerce - Інтернет-магазин

Повнофункціональний інтернет-магазин розроблений на Django з підтримкою оптових та роздрібних цін.

## ✨ Особливості

### 🛒 E-commerce функціонал
- **Каталог товарів** з категоріями та фільтрами
- **Кошик без реєстрації** - сесійний кошик
- **Система замовлень** з різними статусами
- **Роздрібні та оптові ціни** (опт від 5000₴/місяць)
- **Кількісні знижки** для всіх користувачів
- **Акційні товари** з відсотком знижки

### 🎨 Дизайн та UX
- **Адаптивний дизайн** для всіх пристроїв
- **Mobile-first підхід** з особливою увагою до iOS Safari
- **Горизонтальні слайдери** для категорій та товарів
- **Touch-friendly інтерфейс** з swipe жестами
- **Колірна схема**: Яскравий рожевий, золотий, темно-сірий
- **Чистий CSS** без `!important` та конфліктів

### 📱 Мобільна оптимізація
- **iOS Safari сумісність** з safe areas
- **Viewport height фікси** для iPhone
- **Hardware acceleration** для smooth анімацій
- **Touch callout контроль** для кращого UX
- **Zoom prevention** на input focus

### 🔧 Технічні особливості
- **Django 4.2+** з модульною архітектурою apps
- **Українська локалізація** повністю
- **SEO готовність** з мета тегами та структурованими даними
- **Готовність до деплою** на Render
- **Адмін панель** для управління контентом

## 🚀 Швидкий старт

### Встановлення

1. **Клонуйте репозиторій:**
```bash
git clone <your-repository-url>
cd <your-project-folder>
```

2. **Створіть віртуальне середовище:**
```bash
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
```

3. **Встановіть залежності:**
```bash
pip install -r requirements.txt
```

4. **Виконайте міграції:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Створіть суперкористувача:**
```bash
python manage.py createsuperuser
```

6. **Запустіть сервер:**
```bash
python manage.py runserver
```

Сайт буде доступний за адресою: http://127.0.0.1:8000/

## 📁 Структура проекту

```
beautyshop/
├── apps/                    # Django додатки
│   ├── core/               # Основний функціонал
│   ├── products/           # Товари та категорії
│   ├── cart/               # Кошик покупок
│   ├── orders/             # Замовлення
│   ├── users/              # Користувачі
│   └── blog/               # Блог та статті
├── static/                 # Статичні файли
│   ├── css/               # Стилі
│   ├── js/                # JavaScript
│   └── images/            # Зображення
├── templates/             # HTML шаблони
└── beautyshop/           # Налаштування Django
```

## 🎯 Основні сторінки

- **Головна** (`/`) - Hero секція, категорії, рекомендовані товари
- **Каталог** (`/catalog/`) - Всі категорії товарів
- **Кошик** (`/cart/`) - Перегляд та редагування кошика
- **Доставка та оплата** (`/delivery/`) - Інформація про доставку
- **Повернення та обмін** (`/returns/`) - Умови повернення
- **Про нас** (`/about/`) - Інформація про компанію
- **Контакти** (`/contacts/`) - Контактна інформація
- **Адмін панель** (`/admin/`) - Управління контентом

## 🛠 Налаштування для продакшену

### 📧 Налаштування Email

#### Крок 1: Отримання App Password від Gmail
1. Відкрийте Google Account: https://myaccount.google.com/
2. Перейдіть в Security (Безпека)
3. Увімкніть 2-Step Verification (Двоетапна перевірка)
4. Створіть App Password:
   - Перейдіть на https://myaccount.google.com/apppasswords
   - Оберіть "Mail" та "Other (Custom name)"
   - Введіть назву: "Django Shop App"
   - Збережіть згенерований 16-символьний пароль (без пробілів)

#### Крок 2: Створення файлу .env
```bash
cat > .env << 'EOF'
# Development Environment Variables
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
DJANGO_SETTINGS_MODULE=beautyshop.settings.development

# Email Settings для Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=ВСТАВТЕ_ТУТ_ВАШ_APP_PASSWORD
DEFAULT_FROM_EMAIL=Beauty Shop <your-email@gmail.com>

# Site URL
SITE_URL=http://127.0.0.1:8000
EOF
```

### 🚀 Render деплой

#### Швидка інструкція деплою

1. **Підготовка Git репозиторію:**
```bash
git add .
git commit -m "готово для Рендер"
git push origin main
```

2. **Створення аккаунту на Render.com:**
   - Перейдіть на [render.com](https://render.com)
   - Зареєструйтеся або увійдіть
   - Підключіть ваш GitHub/GitLab аккаунт

3. **Деплой через Blueprint (РЕКОМЕНДУЄТЬСЯ!):**
   - На dashboard натисніть "New" → "Blueprint"
   - Підключіть ваш Git репозиторій
   - Render автоматично знайде render.yaml та створить:
     - ✅ PostgreSQL базу даних
     - ✅ Web Service
     - ✅ Всі необхідні змінні середовища
     - ✅ Автоматичний деплоймент
   - Натисніть "Create Blueprint Instance"
   - Дочекайтеся завершення деплойменту (5-10 хвилин)

4. **Перевірка деплойменту:**
   - Відкрийте ваш сайт: https://your-app-name.onrender.com
   - Перевірте адмінку: https://your-app-name.onrender.com/admin/

### 🔐 Адміністративна панель

#### Дані для входу в адмінку:
- **URL:** `/admin/`
- **Username:** `admin`
- **Password:** `admin123`

#### Що доступно в адмінці:
1. **Товари та категорії** (`/admin/products/`)
   - Категорії товарів (ієрархічна структура)
   - Товари (роздрібні та оптові ціни, акції, складські залишки)
   - Множинні зображення товарів

2. **Замовлення** (`/admin/orders/`)
   - Замовлення з повною інформацією
   - Акції та промокоди
   - Підписка на розсилку

3. **Блог** (`/admin/blog/`)
   - Статті з Rich Text редактором (CKEditor)
   - SEO поля та зображення

4. **Користувачі** (`/admin/users/`)
   - Розширений профіль користувача
   - Оптовий/роздрібний статус
   - Місячний оборот (автоматичний розрахунок)

### Змінні середовища для продакшену

Створіть файл `.env` з наступними змінними:

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email для продакшену
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=Beauty Shop <your-email@gmail.com>
```

## 🎨 Кастомізація

### Кольори
Основні кольори визначені в `static/css/base.css`:
```css
:root {
  --primary-pink: #FF1493;      /* Яскравий рожевий */
  --accent-gold: #FFD700;       /* Золотий */
  --neutral-dark: #2C3E50;      /* Темно-сірий */
}
```

### Слайдери
Горизонтальні слайдери налаштовуються в `static/js/sliders.js` та `static/css/sliders.css`.

## 📱 Мобільна підтримка

### iOS Safari
- Safe area підтримка для iPhone X+
- Viewport height фікси
- Touch оптимізації
- Hardware acceleration

### Android Chrome
- Touch action оптимізація
- Overscroll behavior контроль
- High-DPI підтримка

## 🤝 Внесок у розробку

1. Fork репозиторій
2. Створіть feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit зміни (`git commit -m 'Add some AmazingFeature'`)
4. Push до branch (`git push origin feature/AmazingFeature`)
5. Відкрийте Pull Request

## 📄 Ліцензія

Універсальний інтернет-магазин з підтримкою оптових цін.

## 👨‍💻 Розробка

Django E-commerce platform

---

**Django E-commerce** - готовий до використання каркас інтернет-магазину 🛒
