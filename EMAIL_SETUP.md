# 📧 Налаштування Gmail для відправки email

## Крок 1: Отримання App Password від Gmail

### Варіант A: Якщо ви використовуєте Gmail акаунт:

1. **Відкрийте Google Account:** https://myaccount.google.com/
2. **Перейдіть в Security** (Безпека)
3. **Увімкніть 2-Step Verification** (Двоетапна перевірка)
4. **Створіть App Password:**
   - Перейдіть на https://myaccount.google.com/apppasswords
   - Оберіть "Mail" та "Other (Custom name)"
   - Введіть назву: "Beauty Shop Django"
   - Натисніть "Generate"
   - **Збережіть згенерований 16-символьний пароль** (без пробілів)

### Варіант B: Якщо ви використовуєте Ukr.net:

1. Увійдіть в свій акаунт ukr.net
2. Налаштування → Безпека
3. Створіть пароль для додатків
4. Збережіть пароль

## Крок 2: Створення файлу .env

### Створіть файл вручну:

**Використайте команду в терміналі:**

```bash
cd /Users/sofiadmitrenko/Sites/beautyshop

cat > .env << 'EOF'
# Development Environment Variables

# Django Core
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
DJANGO_SETTINGS_MODULE=beautyshop.settings.development

# Email Settings для Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=beauty_shop_monte@ukr.net
EMAIL_HOST_PASSWORD=ВСТАВТЕ_ТУТ_ВАШ_APP_PASSWORD
DEFAULT_FROM_EMAIL=Beauty Shop <beauty_shop_monte@ukr.net>

# Site URL
SITE_URL=http://127.0.0.1:8000
EOF
```

### Або для Ukr.net SMTP:

```bash
cat > .env << 'EOF'
# Development Environment Variables

# Django Core
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
DJANGO_SETTINGS_MODULE=beautyshop.settings.development

# Email Settings для Ukr.net
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.ukr.net
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=beauty_shop_monte@ukr.net
EMAIL_HOST_PASSWORD=ВСТАВТЕ_ТУТ_ВАШ_ПАРОЛЬ_ДЛЯ_ДОДАТКІВ
DEFAULT_FROM_EMAIL=Beauty Shop <beauty_shop_monte@ukr.net>

# Site URL
SITE_URL=http://127.0.0.1:8000
EOF
```

**⚠️ ВАЖЛИВО:**
- Замініть `ВСТАВТЕ_ТУТ_ВАШ_APP_PASSWORD` на ваш App Password
- **НЕ комітьте файл .env в Git!** (він вже в .gitignore)
- Для Ukr.net використовуйте пароль для додатків, НЕ основний пароль

### Після створення файлу, відредагуйте пароль:

```bash
nano .env
# або
open -e .env
```

## Крок 3: Тестування

Після створення `.env` файлу:

1. Перезапустіть сервер Django
2. Спробуйте "Забули пароль?" на сторінці входу
3. Перевірте вашу пошту (також перевірте Spam)

## Наступні кроки:

1. ✅ Створіть `.env` файл з вашими даними
2. ✅ Додайте App Password
3. ✅ Перезапустіть сервер
4. ✅ Протестуйте функціонал

**Готові налаштовувати?** Скажіть коли створите файл `.env`, і я допоможу з тестуванням! 📨

