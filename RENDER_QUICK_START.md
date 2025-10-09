# ⚡ Швидкий старт для Render.com

## 🔑 ЗМІННІ СЕРЕДОВИЩА (Environment Variables)

### Копіюйте та вставляйте на Render → Environment:

```
# Django Settings
DJANGO_SETTINGS_MODULE=beautyshop.settings.production
DEBUG=False

# Hosts & Security
ALLOWED_HOSTS=beautyshop-django.onrender.com,beautyshop-django-*.onrender.com
CSRF_TRUSTED_ORIGINS=https://beautyshop-django.onrender.com
SITE_URL=https://beautyshop-django.onrender.com

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=beautyshop.supp@gmail.com
EMAIL_HOST_PASSWORD=ymycifcxvdrtvrvx
DEFAULT_FROM_EMAIL=Beauty Shop <beautyshop.supp@gmail.com>

# Admin Account
ADMIN_EMAIL=admin@beautyshop.ua
ADMIN_PASSWORD=ВашСильнийПароль123!
```

**⚠️ НЕ ЗАБУДЬТЕ:**
- Змінити `ADMIN_PASSWORD` на свій!
- `EMAIL_HOST_PASSWORD` вводити БЕЗ пробілів

---

## 🚀 Build & Start команди

### Build Command:
```bash
chmod +x build.sh && ./build.sh
```

### Start Command:
```bash
gunicorn beautyshop.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

---

## 🔍 Швидка перевірка після деплою

### 1. Тест головної сторінки:
```
https://beautyshop-django.onrender.com/
```

### 2. Тест адмін панелі:
```
https://beautyshop-django.onrender.com/admin/
Логін: admin@beautyshop.ua
Пароль: (ваш ADMIN_PASSWORD)
```

### 3. Тест email (в Render Shell):
```python
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'beautyshop.supp@gmail.com', ['beautyshop.supp@gmail.com'])
```

---

## 🐛 Швидке вирішення проблем

### Email не працює?
```
Перевірте:
✅ EMAIL_HOST_PASSWORD = ymycifcxvdrtvrvx (без пробілів!)
✅ EMAIL_USE_TLS = True
✅ EMAIL_PORT = 587
```

### 500 Error?
```
Перевірте логи: Web Service → Logs
Шукайте: ALLOWED_HOSTS, DATABASE_URL, SECRET_KEY
```

### Static files не завантажуються?
```
1. Перевірте логи: collectstatic виконався?
2. Очистіть кеш: Ctrl+Shift+R
3. Перезапустіть сервіс: Manual Deploy
```

---

## 📊 Корисні посилання

- **Dashboard:** https://dashboard.render.com
- **Logs:** Web Service → Logs
- **Shell:** Web Service → Shell (вгорі справа)
- **Metrics:** Web Service → Metrics
- **Database Backups:** Database → Backups

---

## ✅ Чеклист

- [ ] PostgreSQL створено
- [ ] Web Service створено
- [ ] 16 змінних середовища додано
- [ ] Деплой успішний
- [ ] Сайт відкривається
- [ ] Admin працює
- [ ] Email надсилається

**Детальна інструкція:** `RENDER_DEPLOYMENT_GUIDE.md`

