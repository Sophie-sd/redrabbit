# ПЛАН ІМПЛЕМЕНТАЦІЇ: redrabbit — Оновлення проекту

## АНАЛІЗ ІСНУЮЧОГО КОДУ

### ✅ ЩО ВЖЕ РЕАЛІЗОВАНО

**Моделі БД:**
- `Category` (parent-child, external_id, is_active, sort_order, SEO)
- `Product` (external_id, vendor_name, is_sale, sale_price, is_top, is_new, stock)
- `ProductImage` (is_main, sort_order, автооптимізація до 800px)
- `ProductAttribute` (характеристики товарів)
- `ProductTag` (теги для фільтрації)
- `Banner` (desktop/mobile images, order, is_active)
- `Order`, `OrderItem` (базова структура замовлень)
- `Promotion`, `Newsletter` (акції та розсилка)

**Views:**
- `HomeView` (банери, новинки, акції, хіти)
- `CatalogView` (список категорій)
- `CategoryView` (товари категорії, пагінація)
- `ProductDetailView` (деталі товару)
- `SaleProductsView` (акційні товари)
- `SearchView` (пошук товарів)

**Templates:**
- `base.html` (базовий шаблон, SEO meta, structured data)
- `includes/header.html` (logo, search, wishlist, cart)
- `includes/footer.html` (4 колонки, підписка)
- `core/home.html` (banner slider, promotions, features, new products)

**Frontend:**
- CSS variables system (`variables.css`)
- 26 CSS файлів (base, components, mobile, sliders тощо)
- 17 JS файлів (utils, cart, wishlist, sliders тощо)
- Banner slider (автопрокрутка, навігація)
- Promotions slider, Recommended slider
- Mobile menu, mobile search
- Cart integration, Wishlist

**Context Processors:**
- `base_context` (main_categories, cart, site info)
- `wishlist` context processor

**Management Commands:**
- `import_products` (XML імпорт з SMTM)
- `update_prices` (CSV оновлення цін)
- `import_categories`, `create_categories`

**Інше:**
- Cloudinary налаштовано
- Whitenoise для статики
- Session cart та wishlist
- Google Analytics placeholder

---

## 🔴 ЩО ТРЕБА ДОДАТИ/ЗМІНИТИ

### КРИТИЧНІ ЗМІНИ

**1. Нові моделі:**
- `ProductReview` (відгуки користувачів)
- `Brand` (бренди для блоку "Бренди")
- Розширити `Order` (nova_poshta_ttn, payment_intent_id, monobank_parts)
- Додати `video_url` в `Product` (для бейджа "ВІДЕО")

**2. Age Verification Modal (18+):**
- Новий JS файл: `age-verification.js`
- Новий CSS файл: `age-verification.css`
- Cookie `age_verified` (термін 24 год)

**3. Ребрендинг на redrabbit:**
- Змінити всі кольори в `variables.css`
- Оновити logo
- Змінити назву сайту в templates
- Оновити favicon

**4. Новий Header:**
- Додати номер телефону
- Змінити placeholder пошуку
- Live search автокомпліт (AJAX)
- Sticky header

**5. Sidebar Menu (категорії):**
- Новий template: `includes/sidebar-menu.html`
- Новий CSS: `sidebar-menu.css`
- Новий JS: `sidebar-menu.js` (розкриття підкатегорій)
- Інтеграція на головній та каталозі

**6. Блок "Лідери продажу":**
- Використати існуючий slider
- View: фільтр `is_top=True` або `is_featured=True`
- Template секція в `home.html`

**7. Блок "Бренди":**
- Модель `Brand` (name, slug, logo, is_active, sort_order)
- Admin для Brand
- Template секція
- CSS: `brands-section.css`
- View: передати бренди в context

**8. Блок "Відгуки":**
- Модель `ProductReview` (product, author_name, rating, text, category_badge, is_approved)
- Admin для ProductReview
- Template: slider відгуків
- CSS: `reviews-section.css`
- JS: `reviews-slider.js`

**9. Інформаційні банери:**
- Оновити існуючу Features секцію
- 3 нові іконки (замок, коробка, телефон)
- Оновити тексти згідно ТЗ

**10. Footer:**
- Переробити структуру (4 колонки)
- Додати графік роботи (Пн-Сб 9-18)
- Додати іконки соцмереж (placeholder)
- Логотипи платіжних систем

**11. Сторінка товару:**
- Галерея з zoom
- Блок варіантів (колір)
- Покупка в кредит (Monobank)
- Блок доставки (accordion)
- Блок оплати (логотипи)
- Табби (Опис, Характеристики, Відгуки, Питання)
- Кнопки: Купити, Порівняти, Обране, Share

**12. Сторінка каталогу:**
- Фільтри (ціна, бренд, наявність, рейтинг, акції)
- Сортування (5 варіантів)
- Хлібні крихти
- Пагінація або infinite scroll

**13. Сторінка пошуку:**
- Обробка 0 результатів
- Блок "Рекомендовані товари"

---

## 📋 ПЛАН РЕАЛІЗАЦІЇ ПО ФАЗАХ

### ФАЗА 0: ПІДГОТОВКА (1 день)

#### 0.1. Створити backup БД
```bash
python manage.py dumpdata > backup_before_rebrand.json
```

#### 0.2. Створити нові моделі

**Файл:** `apps/products/models.py`
**Дія:** Додати поля в кінець класу `Product`:
```python
video_url = URLField(blank=True, help_text='YouTube або Vimeo URL')
```

**Файл:** `apps/products/models.py` (нова модель)
**Дія:** Створити модель `ProductReview`:
```python
class ProductReview(models.Model):
    product = ForeignKey(Product, on_delete=CASCADE, related_name='reviews')
    author_name = CharField(max_length=100, default="Аноним")
    rating = PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = TextField()
    category_badge = CharField(max_length=50, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    is_approved = BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
```

**Файл:** `apps/products/models.py` (нова модель)
**Дія:** Створити модель `Brand`:
```python
class Brand(models.Model):
    name = CharField(max_length=100, unique=True)
    slug = SlugField(unique=True, blank=True)
    logo = ImageField(upload_to='brands/', blank=True)
    description = TextField(blank=True)
    is_active = BooleanField(default=True)
    sort_order = PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

**Файл:** `apps/orders/models.py`
**Дія:** Розширити модель `Order` (додати поля в кінець):
```python
nova_poshta_ttn = CharField(max_length=50, blank=True)
payment_intent_id = CharField(max_length=100, blank=True)
monobank_parts = BooleanField(default=False)
```

#### 0.3. Міграції
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 0.4. Зареєструвати моделі в admin

**Файл:** `apps/products/admin.py`
**Дія:** Додати в кінець:
```python
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'author_name', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['product__name', 'author_name', 'text']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'sort_order']
    list_editable = ['is_active', 'sort_order']
    prepopulated_fields = {'slug': ('name',)}
```

---

### ФАЗА 1: РЕБРЕНДИНГ НА redrabbit (1-2 дні)

#### 1.1. Оновити CSS variables

**Файл:** `static/css/variables.css`
**Дія:** Замінити секцію кольорів (рядки 6-62):
```css
:root {
  /* ========== REDRABBIT КОЛЬОРИ (60-30-10) ========== */
  
  /* 60% - ФОНОВІ */
  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F2E8DA;  /* Pristine */
  --color-bg-tertiary: #FAFAFA;
  
  /* 30% - БРЕНДОВІ */
  --color-brand-primary: #FA9A85;    /* Peach Pink */
  --color-brand-light: #FFBE98;      /* Peach Fuzz */
  --color-brand-accent: #E881A6;     /* Aurora Pink */
  --color-brand-mint: #60C8B3;       /* Bermuda */
  --color-brand-purple: #B380AA;     /* Pale Pansy */
  
  /* 10% - АКЦЕНТНІ (CTA) */
  --color-cta-primary: #E53935;      /* Червоний */
  --color-cta-coral: #F97272;        /* Georgia Peach */
  
  /* ТЕКСТОВІ */
  --color-text-primary: #2C2C2C;
  --color-text-secondary: #6B6B6B;
  --color-text-muted: #999999;
  --color-text-white: #FFFFFF;
  
  /* СИСТЕМНІ */
  --color-success: #60C8B3;  /* Bermuda */
  --color-warning: #FFB74D;
  --color-error: #E53935;
  --color-info: #B380AA;
  
  /* БОРДЕРИ */
  --color-border-light: #E0E0E0;
  --color-border-medium: #BDBDBD;
  --color-border-dark: #757575;
  
  /* БЕЙДЖІ */
  --badge-top: #FFD700;      /* Жовтий "ТОП ПРОДАЖ" */
  --badge-sale: #F97272;     /* Georgia Peach "-X%" */
  --badge-video: #4285F4;    /* Синій "ВІДЕО" */
  --badge-new: #60C8B3;      /* Bermuda "НОВИНКА" */
  
  /* Legacy aliases (видалити старі, додати нові) */
  --primary-color: var(--color-cta-primary);
  --primary-pink: var(--color-brand-primary);
  --accent-gold: var(--color-brand-accent);
  --neutral-dark: var(--color-text-primary);
  --white: var(--color-bg-primary);
  --success: var(--color-success);
  --danger: var(--color-error);
}
```

#### 1.2. Створити logo redrabbit

**Файл:** `static/images/logo-redrabbit.png`
**Дія:** Створити або отримати логотип (200x60px)
**Альтернатива:** Text logo в CSS:
```css
/* static/css/components.min.css */
.logo-redrabbit {
  font-family: var(--font-heading);
  font-size: 24px;
  font-weight: 700;
  color: var(--color-cta-primary);
}
.logo-redrabbit span {
  color: var(--color-brand-primary);
}
```

#### 1.3. Оновити назву сайту

**Файл:** `apps/core/context_processors.py`
**Рядок 14:** Замінити:
```python
'site_name': 'redrabbit',
```

**Файл:** `templates/base.html`
**Рядок 9:** Замінити:
```html
<title>{% block title %}redrabbit - Інтернет-магазин інтимних товарів{% endblock %}</title>
```

**Рядок 12:** Змінити author:
```html
<meta name="author" content="redrabbit">
```

**Рядок 93-95:** Змінити structured data:
```json
"name": "redrabbit",
```

#### 1.4. Оновити favicon

**Файли:** `static/images/favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`
**Дія:** Створити іконки з кроликом або літерами "rr"

---

### ФАЗА 2: AGE VERIFICATION MODAL (1 день)

#### 2.1. Створити CSS для модалки

**Файл:** `static/css/age-verification.css` (НОВИЙ)
**Вміст:**
```css
/* Age Verification Modal */
.age-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;
}

.age-modal {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xxl);
  max-width: 500px;
  width: 90%;
  box-shadow: var(--shadow-xl);
  text-align: center;
  transform: scale(0.9);
  animation: scaleIn 0.3s ease 0.2s forwards;
}

.age-modal__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-cta-primary);
  margin-bottom: var(--spacing-md);
}

.age-modal__text {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
  line-height: var(--line-height-relaxed);
}

.age-modal__buttons {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
}

.age-modal__btn {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  min-width: 150px;
  border: none;
}

.age-modal__btn--confirm {
  background: var(--color-cta-primary);
  color: var(--color-text-white);
}

.age-modal__btn--confirm:hover {
  background: #C62828;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.age-modal__btn--deny {
  background: var(--color-bg-primary);
  color: var(--color-cta-primary);
  border: 2px solid var(--color-cta-primary);
}

.age-modal__btn--deny:hover {
  background: var(--color-bg-secondary);
}

@keyframes fadeIn {
  to { opacity: 1; }
}

@keyframes scaleIn {
  to { transform: scale(1); }
}

@media (max-width: 768px) {
  .age-modal {
    padding: var(--spacing-xl);
  }
  .age-modal__buttons {
    flex-direction: column;
  }
  .age-modal__btn {
    width: 100%;
  }
}
```

#### 2.2. Створити JS для модалки

**Файл:** `static/js/age-verification.js` (НОВИЙ)
**Вміст:**
```javascript
(function() {
  'use strict';
  
  const AGE_COOKIE_NAME = 'age_verified';
  const AGE_COOKIE_DAYS = 1;
  
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }
  
  function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/;SameSite=Strict`;
  }
  
  function showAgeModal() {
    const overlay = document.createElement('div');
    overlay.className = 'age-modal-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-labelledby', 'age-modal-title');
    
    overlay.innerHTML = `
      <div class="age-modal">
        <h2 class="age-modal__title" id="age-modal-title">УВАГА!</h2>
        <p class="age-modal__text">
          Цей сайт містить матеріали для дорослих. 
          Щоб продовжити, підтвердіть, що вам виповнилося 18 років.
        </p>
        <div class="age-modal__buttons">
          <button class="age-modal__btn age-modal__btn--deny" id="ageDenyBtn">
            Ні, мені менше 18 років
          </button>
          <button class="age-modal__btn age-modal__btn--confirm" id="ageConfirmBtn">
            Так, мені вже є 18
          </button>
        </div>
      </div>
    `;
    
    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';
    
    // Заборонити закриття ESC або кліком поза модалкою
    overlay.addEventListener('click', (e) => {
      e.stopPropagation();
    });
    
    document.getElementById('ageConfirmBtn').addEventListener('click', () => {
      setCookie(AGE_COOKIE_NAME, '1', AGE_COOKIE_DAYS);
      overlay.style.animation = 'fadeOut 0.3s ease forwards';
      setTimeout(() => {
        overlay.remove();
        document.body.style.overflow = '';
      }, 300);
    });
    
    document.getElementById('ageDenyBtn').addEventListener('click', () => {
      window.location.href = 'https://www.google.com';
    });
  }
  
  // Перевірка при завантаженні сторінки
  if (!getCookie(AGE_COOKIE_NAME)) {
    // Затримка для кращого UX
    setTimeout(showAgeModal, 500);
  }
})();
```

#### 2.3. Додати в base.html

**Файл:** `templates/base.html`
**Після рядка 82:** Додати:
```html
<link rel="stylesheet" href="{% static 'css/age-verification.css' %}">
```

**Перед рядком 186 (перед GA):** Додати:
```html
<script src="{% static 'js/age-verification.js' %}"></script>
```

---

### ФАЗА 3: HEADER ОНОВЛЕННЯ (1 день)

#### 3.1. Оновити header template

**Файл:** `templates/includes/header.html`
**Дія:** Замінити секцію Search (рядки 14-34):
```html
<!-- Search with Live Autocomplete -->
<div class="search-container">
    <form action="{% url 'core:search' %}" method="get" class="search-form" role="search">
        <div class="search-input-group">
            <input 
                type="search" 
                name="q" 
                placeholder="Запали в собі вогонь... 🔥" 
                class="search-input"
                value="{{ request.GET.q|default:'' }}"
                aria-label="Пошук товарів"
                autocomplete="off"
                id="searchInput"
            >
            <div class="search-autocomplete" id="searchAutocomplete"></div>
            <button type="submit" class="search-btn" aria-label="Знайти">
                <svg class="search-icon" viewBox="0 0 24 24">
                    <path d="M21 21L16.514 16.506M19 10.5C19 15.194 15.194 19 10.5 19C5.806 19 2 15.194 2 10.5C2 5.806 5.806 2 10.5 2C15.194 2 19 5.806 19 10.5Z" stroke="currentColor" stroke-width="2"/>
                </svg>
            </button>
        </div>
    </form>
</div>

<!-- Phone -->
<div class="header-phone desktop-only">
    <a href="tel:+380XXXXXXXXX" class="phone-link">
        <svg class="phone-icon" viewBox="0 0 24 24" width="20" height="20">
            <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z" fill="none" stroke="currentColor" stroke-width="2"/>
        </svg>
        <span class="phone-number">+38 XXX XXX XX XX</span>
    </a>
</div>
```

#### 3.2. Створити Live Search JS

**Файл:** `static/js/live-search.js` (НОВИЙ)
**Вміст:**
```javascript
(function() {
  'use strict';
  
  const searchInput = document.getElementById('searchInput');
  const autocomplete = document.getElementById('searchAutocomplete');
  let debounceTimer;
  
  if (!searchInput || !autocomplete) return;
  
  searchInput.addEventListener('input', function() {
    const query = this.value.trim();
    
    clearTimeout(debounceTimer);
    
    if (query.length < 2) {
      autocomplete.innerHTML = '';
      autocomplete.classList.remove('active');
      return;
    }
    
    debounceTimer = setTimeout(() => {
      fetch(`/api/search/autocomplete/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          if (data.results && data.results.length > 0) {
            autocomplete.innerHTML = data.results.map(item => `
              <a href="${item.url}" class="autocomplete-item">
                <img src="${item.image}" alt="${item.name}" loading="lazy">
                <span class="autocomplete-name">${item.name}</span>
                <span class="autocomplete-price">${item.price} ₴</span>
              </a>
            `).join('');
            autocomplete.classList.add('active');
          } else {
            autocomplete.innerHTML = '<div class="autocomplete-empty">Нічого не знайдено</div>';
            autocomplete.classList.add('active');
          }
        });
    }, 300);
  });
  
  // Закрити при кліку поза
  document.addEventListener('click', function(e) {
    if (!searchInput.contains(e.target) && !autocomplete.contains(e.target)) {
      autocomplete.classList.remove('active');
    }
  });
})();
```

#### 3.3. Створити API endpoint для автокомпліту

**Файл:** `apps/core/views.py`
**Додати в кінець:**
```python
from django.http import JsonResponse

def search_autocomplete(request):
    """API для автокомпліту пошуку"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query),
        is_active=True
    )[:5]
    
    results = [{
        'name': p.name,
        'url': p.get_absolute_url(),
        'price': str(p.get_current_price()),
        'image': p.main_image.image.url if p.main_image else '/static/images/placeholder.png'
    } for p in products]
    
    return JsonResponse({'results': results})
```

**Файл:** `apps/core/urls.py`
**Додати:**
```python
path('api/search/autocomplete/', views.search_autocomplete, name='search_autocomplete'),
```

#### 3.4. Sticky header CSS

**Файл:** `static/css/components.min.css` або створити `header-sticky.css`
**Додати:**
```css
.header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.header.scrolled {
  box-shadow: var(--shadow-md);
}

.search-autocomplete {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
  border-top: none;
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  max-height: 400px;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
  display: none;
  z-index: 100;
}

.search-autocomplete.active {
  display: block;
}

.autocomplete-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border-light);
  transition: background var(--transition-fast);
}

.autocomplete-item:hover {
  background: var(--color-bg-secondary);
}

.autocomplete-item img {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: var(--radius-sm);
}

.autocomplete-name {
  flex: 1;
  font-size: var(--font-size-sm);
}

.autocomplete-price {
  font-weight: var(--font-weight-semibold);
  color: var(--color-cta-primary);
}

.header-phone {
  display: flex;
  align-items: center;
  margin-left: var(--spacing-md);
}

.phone-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--color-text-primary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: color var(--transition-fast);
}

.phone-link:hover {
  color: var(--color-cta-primary);
}

.phone-number {
  font-weight: var(--font-weight-semibold);
}

@media (max-width: 768px) {
  .desktop-only {
    display: none;
  }
}
```

---

### ФАЗА 4: SIDEBAR MENU (1 день)

#### 4.1. Створити template sidebar

**Файл:** `templates/includes/sidebar-menu.html` (НОВИЙ)
**Вміст:**
```django
{% load static %}

<aside class="sidebar-menu" role="navigation" aria-label="Категорії товарів">
    <ul class="sidebar-menu__list">
        {% for category in main_categories %}
        <li class="sidebar-menu__item {% if category.children.exists %}has-children{% endif %}">
            <a href="{{ category.get_absolute_url }}" class="sidebar-menu__link">
                <span class="sidebar-menu__icon">
                    {% comment %} Іконки додати пізніше {% endcomment %}
                    <svg width="20" height="20" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
                    </svg>
                </span>
                <span class="sidebar-menu__text">{{ category.name }}</span>
                {% if category.children.exists %}
                <span class="sidebar-menu__arrow">→</span>
                {% endif %}
            </a>
            
            {% if category.children.exists %}
            <div class="sidebar-menu__submenu">
                <ul class="submenu__list">
                    {% for child in category.children.all %}
                    {% if child.is_active %}
                    <li class="submenu__item">
                        <a href="{{ child.get_absolute_url }}" class="submenu__link">
                            {{ child.name }}
                        </a>
                    </li>
                    {% endif %}
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </li>
        {% endfor %}
    </ul>
</aside>
```

#### 4.2. Створити CSS для sidebar

**Файл:** `static/css/sidebar-menu.css` (НОВИЙ)
**Вміст:**
```css
.sidebar-menu {
  width: 280px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  position: sticky;
  top: calc(var(--header-height, 80px) + var(--spacing-md));
  align-self: flex-start;
}

.sidebar-menu__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-menu__item {
  position: relative;
  margin-bottom: var(--spacing-xs);
}

.sidebar-menu__link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-primary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  font-size: var(--font-size-base);
}

.sidebar-menu__link:hover {
  background: rgba(250, 154, 133, 0.1);  /* Peach Pink з прозорістю */
  color: var(--color-cta-primary);
}

.sidebar-menu__item.active > .sidebar-menu__link {
  background: var(--color-brand-primary);
  color: var(--color-text-white);
}

.sidebar-menu__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--color-brand-primary);
}

.sidebar-menu__text {
  flex: 1;
  font-weight: var(--font-weight-medium);
}

.sidebar-menu__arrow {
  font-size: 18px;
  color: var(--color-brand-accent);
  transition: transform var(--transition-fast);
}

.sidebar-menu__item.has-children:hover .sidebar-menu__arrow {
  transform: translateX(4px);
}

/* Підменю */
.sidebar-menu__submenu {
  max-height: 0;
  overflow: hidden;
  transition: max-height var(--transition-normal);
  margin-top: var(--spacing-xs);
}

.sidebar-menu__item:hover .sidebar-menu__submenu {
  max-height: 600px;
}

.submenu__list {
  list-style: none;
  padding: 0;
  margin: 0;
  padding-left: var(--spacing-xl);
}

.submenu__link {
  display: block;
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.submenu__link:hover {
  background: var(--color-bg-primary);
  color: var(--color-cta-primary);
  padding-left: calc(var(--spacing-md) + 4px);
}

/* Mobile */
@media (max-width: 992px) {
  .sidebar-menu {
    display: none;  /* На мобільних використовувати mobile-menu */
  }
}
```

#### 4.3. Інтегрувати sidebar в home.html

**Файл:** `templates/core/home.html`
**Після рядка 7 (після {% block content %}):** Додати:
```django
<div class="container">
    <div class="home-layout">
        <!-- Sidebar -->
        <div class="home-layout__sidebar">
            {% include 'includes/sidebar-menu.html' %}
        </div>
        
        <!-- Main Content -->
        <div class="home-layout__content">
```

**Перед {% endblock %} (в кінці):** Додати:
```django
        </div>  <!-- /.home-layout__content -->
    </div>  <!-- /.home-layout -->
</div>  <!-- /.container -->
```

#### 4.4. CSS для home layout

**Файл:** `static/css/layout.min.css` або створити `home-layout.css`
**Додати:**
```css
.home-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-lg);
}

.home-layout__sidebar {
  /* Sidebar sticky в CSS sidebar-menu.css */
}

.home-layout__content {
  min-width: 0;  /* Запобігає переповненню grid */
}

@media (max-width: 992px) {
  .home-layout {
    grid-template-columns: 1fr;
  }
  
  .home-layout__sidebar {
    display: none;
  }
}
```

---

### ФАЗА 5: БЛОК "ЛІДЕРИ ПРОДАЖУ" (0.5 дня)

#### 5.1. Додати секцію в home.html

**Файл:** `templates/core/home.html`
**Після секції "Акції" (після рядка ~221):** Додати:
```django
<!-- Top Products Section -->
<section class="top-products-section section-padding" aria-label="Лідери продажу">
    <div class="container">
        <div class="section-header text-center">
            <h2 class="section-title">Лідери продажу</h2>
            <p class="section-subtitle">Найпопулярніші товари серед наших клієнтів</p>
        </div>
        
        {% if top_products %}
        <div class="product-slider-container">
            <button class="slider-nav-btn slider-prev-btn" aria-label="Попередні товари">
                <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2"/>
                </svg>
            </button>
            
            <div class="product-slider" id="topProductsSlider">
                {% for product in top_products %}
                    {% include 'includes/product-card.html' with product=product %}
                {% endfor %}
            </div>
            
            <button class="slider-nav-btn slider-next-btn" aria-label="Наступні товари">
                <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2"/>
                </svg>
            </button>
        </div>
        {% else %}
            <p class="text-center text-muted">Наразі немає товарів</p>
        {% endif %}
    </div>
</section>
```

#### 5.2. View вже передає top_products

**Файл:** `apps/core/views.py`
**Рядки 34-38:** Вже є, перевірити що працює

---

### ФАЗА 6: БЛОК "БРЕНДИ" (1 день)

#### 6.1. Створити template секцію

**Файл:** `templates/core/home.html`
**Після блоку "Лідери продажу":** Додати:
```django
<!-- Brands Section -->
<section class="brands-section section-padding bg-light" aria-label="Бренди">
    <div class="container">
        <div class="section-header text-center">
            <h2 class="section-title">Бренди</h2>
            <p class="section-subtitle">Працюємо з найкращими виробниками</p>
        </div>
        
        {% if brands %}
        <div class="brands-grid">
            {% for brand in brands %}
            <a href="{% url 'core:catalog' %}?brand={{ brand.slug }}" class="brand-card">
                <div class="brand-card__logo">
                    {% if brand.logo %}
                        <img src="{{ brand.logo.url }}" alt="{{ brand.name }}" loading="lazy">
                    {% else %}
                        <div class="brand-placeholder">{{ brand.name|slice:":2"|upper }}</div>
                    {% endif %}
                </div>
                <div class="brand-card__name">{{ brand.name }}</div>
            </a>
            {% endfor %}
        </div>
        
        <div class="text-center mt-4">
            <a href="{% url 'core:brands' %}" class="btn btn-secondary">
                Всі бренди
            </a>
        </div>
        {% endif %}
    </div>
</section>
```

#### 6.2. Створити CSS для брендів

**Файл:** `static/css/brands-section.css` (НОВИЙ)
**Вміст:**
```css
.brands-section {
  background: var(--color-bg-secondary);
}

.brands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--spacing-lg);
  max-width: 1000px;
  margin: 0 auto;
}

.brand-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  text-decoration: none;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.brand-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.brand-card__logo {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-round);
  background: var(--color-bg-tertiary);
  padding: var(--spacing-md);
}

.brand-card__logo img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.brand-placeholder {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-brand-primary);
}

.brand-card__name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  text-align: center;
}

@media (max-width: 768px) {
  .brands-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: var(--spacing-md);
  }
  
  .brand-card__logo {
    width: 80px;
    height: 80px;
  }
}
```

#### 6.3. Додати brands в HomeView

**Файл:** `apps/core/views.py`
**Рядок 45 (після top_products):** Додати:
```python
from apps.products.models import Brand

# В контексті:
'brands': Brand.objects.filter(is_active=True).order_by('sort_order', 'name')[:8],
```

#### 6.4. Створити сторінку всіх брендів

**Файл:** `apps/core/views.py`
**Додати:**
```python
class BrandsView(TemplateView):
    """Всі бренди"""
    template_name = 'core/brands.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.filter(is_active=True).order_by('sort_order', 'name')
        return context
```

**Файл:** `templates/core/brands.html` (НОВИЙ)
**Вміст:** (копія brands-section але без обмеження на 8)

#### 6.5. Додати URL

**Файл:** `apps/core/urls.py`
**Додати:**
```python
path('brands/', views.BrandsView.as_view(), name='brands'),
```

---

### ФАЗА 7: БЛОК "ВІДГУКИ" (1 день)

#### 7.1. Створити template секцію

**Файл:** `templates/core/home.html`
**Після блоку "Бренди":** Додати:
```django
<!-- Reviews Section -->
<section class="reviews-section section-padding" aria-label="Відгуки користувачів">
    <div class="container">
        <div class="section-header text-center">
            <h2 class="section-title">Відгуки користувачів</h2>
            <p class="section-subtitle">Що кажуть наші клієнти</p>
        </div>
        
        {% if reviews %}
        <div class="reviews-slider-container">
            <button class="slider-nav-btn slider-prev-btn" aria-label="Попередні відгуки">
                <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2"/>
                </svg>
            </button>
            
            <div class="reviews-slider" id="reviewsSlider">
                {% for review in reviews %}
                <div class="review-card">
                    {% if review.category_badge %}
                    <span class="review-badge">{{ review.category_badge }}</span>
                    {% endif %}
                    
                    <div class="review-product">
                        <div class="review-product__image">
                            {% if review.product.main_image %}
                                <img src="{{ review.product.main_image.image.url }}" alt="{{ review.product.name }}" loading="lazy">
                            {% endif %}
                        </div>
                        <a href="{{ review.product.get_absolute_url }}" class="review-product__name">
                            {{ review.product.name }}
                        </a>
                    </div>
                    
                    <div class="review-text">
                        <p>{{ review.text|truncatewords:30 }}</p>
                        {% if review.text|wordcount > 30 %}
                        <button class="review-more">Більше...</button>
                        {% endif %}
                    </div>
                    
                    <div class="review-footer">
                        <div class="review-author">
                            <span class="review-author__icon">👤</span>
                            <span class="review-author__name">{{ review.author_name }}</span>
                        </div>
                        <div class="review-rating">
                            {% for i in "12345" %}
                                <span class="star {% if forloop.counter <= review.rating %}active{% endif %}">⭐</span>
                            {% endfor %}
                        </div>
                        <div class="review-date">
                            📅 {{ review.created_at|date:"d F Y" }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <button class="slider-nav-btn slider-next-btn" aria-label="Наступні відгуки">
                <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2"/>
                </svg>
            </button>
        </div>
        {% endif %}
    </div>
</section>
```

#### 7.2. Створити CSS для відгуків

**Файл:** `static/css/reviews-section.css` (НОВИЙ)
**Вміст:**
```css
.reviews-slider-container {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
}

.reviews-slider {
  display: flex;
  gap: var(--spacing-lg);
  overflow-x: auto;
  scroll-behavior: smooth;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.reviews-slider::-webkit-scrollbar {
  display: none;
}

.review-card {
  min-width: 320px;
  max-width: 350px;
  padding: var(--spacing-lg);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  position: relative;
}

.review-badge {
  position: absolute;
  top: var(--spacing-sm);
  left: var(--spacing-sm);
  padding: 4px 12px;
  background: var(--color-brand-accent);
  color: var(--color-text-white);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-md);
}

.review-product {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  padding-top: var(--spacing-lg);
}

.review-product__image {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.review-product__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-md);
}

.review-product__name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.review-product__name:hover {
  color: var(--color-cta-primary);
}

.review-text {
  margin-bottom: var(--spacing-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
}

.review-more {
  background: none;
  border: none;
  color: var(--color-brand-primary);
  cursor: pointer;
  font-size: var(--font-size-sm);
  padding: 0;
}

.review-footer {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

.review-author {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.review-rating {
  display: flex;
  gap: 2px;
}

.star {
  font-size: 16px;
  opacity: 0.3;
}

.star.active {
  opacity: 1;
}

.review-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .review-card {
    min-width: 280px;
  }
}
```

#### 7.3. Створити JS для слайдера відгуків

**Файл:** `static/js/reviews-slider.js` (НОВИЙ)
**Вміст:**
```javascript
(function() {
  'use strict';
  
  const slider = document.getElementById('reviewsSlider');
  if (!slider) return;
  
  const prevBtn = slider.closest('.reviews-slider-container').querySelector('.slider-prev-btn');
  const nextBtn = slider.closest('.reviews-slider-container').querySelector('.slider-next-btn');
  
  const scrollAmount = 350;
  
  nextBtn?.addEventListener('click', () => {
    slider.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  });
  
  prevBtn?.addEventListener('click', () => {
    slider.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  });
  
  // "Більше..." expand
  document.querySelectorAll('.review-more').forEach(btn => {
    btn.addEventListener('click', function() {
      const text = this.closest('.review-text');
      text.querySelector('p').style.display = 'block';
      text.querySelector('p').style.webkitLineClamp = 'unset';
      this.remove();
    });
  });
})();
```

#### 7.4. Додати reviews в HomeView

**Файл:** `apps/core/views.py`
**Додати:**
```python
from apps.products.models import ProductReview

# В контексті:
'reviews': ProductReview.objects.filter(
    is_approved=True
).select_related('product').prefetch_related('product__images').order_by('-created_at')[:10],
```

---

### ФАЗА 8: ОНОВИТИ FEATURES СЕКЦІЮ (0.5 дня)

#### 8.1. Оновити existing features

**Файл:** `templates/core/home.html`
**Рядки 224-258:** Замінити:
```django
<!-- Features Section -->
<section class="features-section section-padding" aria-label="Наші переваги">
    <div class="container">
        <div class="features-grid">
            <div class="feature-item fade-in">
                <div class="feature-image">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
                        <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
                        <path d="M7 11V7C7 4.23858 9.23858 2 12 2C14.7614 2 17 4.23858 17 7V11" stroke="currentColor" stroke-width="2"/>
                    </svg>
                </div>
                <div class="feature-content">
                    <h3 class="feature-title">Захист персональних даних</h3>
                    <p class="feature-description">Не зберігаємо Ваші персональні дані, не використовуємо їх</p>
                </div>
            </div>
            
            <div class="feature-item fade-in">
                <div class="feature-image">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
                        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" stroke="currentColor" stroke-width="2"/>
                    </svg>
                </div>
                <div class="feature-content">
                    <h3 class="feature-title">Безпечна доставка</h3>
                    <p class="feature-description">Не маркуємо коробки при відправці, при відправці назву як сумерр</p>
                </div>
            </div>
            
            <div class="feature-item fade-in">
                <div class="feature-image">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
                        <rect x="5" y="2" width="14" height="20" rx="2" stroke="currentColor" stroke-width="2"/>
                        <path d="M12 18h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <div class="feature-content">
                    <h3 class="feature-title">Без спаму в месенджерах</h3>
                    <p class="feature-description">Не розсилаємо спам Вам на телефон, не робимо розсилки</p>
                </div>
            </div>
        </div>
    </div>
</section>
```

#### 8.2. Оновити CSS features

**Файл:** `static/css/features.css`
**Дія:** Перевірити що використовує нові кольори з variables.css

---

### ФАЗА 9: FOOTER ОНОВЛЕННЯ (0.5 дня)

#### 9.1. Оновити footer template

**Файл:** `templates/includes/footer.html`
**Замінити весь вміст:**
```django
{% load static %}

<div class="footer-main">
    <div class="container">
        <div class="footer-grid">
            <!-- Колонка 1: Інформація -->
            <div class="footer-col">
                <h4 class="footer-title">ІНФОРМАЦІЯ</h4>
                <ul class="footer-links">
                    <li><a href="{% url 'core:about' %}">Про нас</a></li>
                    <li><a href="{% url 'core:delivery' %}">Доставка та оплата</a></li>
                    <li><a href="{% url 'core:returns' %}">Повернення та обмін</a></li>
                    <li><a href="{% url 'core:contacts' %}">Контакти</a></li>
                </ul>
            </div>
            
            <!-- Колонка 2: Каталог -->
            <div class="footer-col">
                <h4 class="footer-title">КАТАЛОГ</h4>
                <ul class="footer-links">
                    {% for category in main_categories|slice:":6" %}
                    <li><a href="{{ category.get_absolute_url }}">{{ category.name }}</a></li>
                    {% endfor %}
                    <li><a href="{% url 'products:sale' %}">Акції</a></li>
                    <li><a href="{% url 'core:brands' %}">Бренди</a></li>
                </ul>
            </div>
            
            <!-- Колонка 3: Клієнтам -->
            <div class="footer-col">
                <h4 class="footer-title">КЛІЄНТАМ</h4>
                <ul class="footer-links">
                    <li><a href="{% url 'core:terms' %}">Умови використання</a></li>
                    <li><a href="{% url 'core:privacy' %}">Політика конфіденційності</a></li>
                </ul>
                <div class="footer-schedule">
                    <p class="footer-schedule__title">Графік роботи:</p>
                    <p>Пн-Сб: 9:00-18:00</p>
                    <p>Нд: Вихідний</p>
                </div>
            </div>
            
            <!-- Колонка 4: Контакти та соцмережі -->
            <div class="footer-col">
                <h4 class="footer-title">КОНТАКТИ</h4>
                <div class="footer-contact">
                    <p class="footer-phone">
                        <a href="tel:+380XXXXXXXXX">+38 XXX XXX XX XX</a>
                    </p>
                    <p class="footer-email">
                        <a href="mailto:info@redrabbit.com">info@redrabbit.com</a>
                    </p>
                </div>
                
                <div class="footer-social">
                    <p class="footer-social__title">Ми в соцмережах:</p>
                    <div class="social-links">
                        <a href="#" class="social-link" aria-label="Instagram" title="Instagram">
                            <svg width="24" height="24" viewBox="0 0 24 24"><path d="M..." fill="currentColor"/></svg>
                        </a>
                        <a href="#" class="social-link" aria-label="Facebook" title="Facebook">
                            <svg width="24" height="24" viewBox="0 0 24 24"><path d="M..." fill="currentColor"/></svg>
                        </a>
                        <a href="#" class="social-link" aria-label="Threads" title="Threads">
                            <svg width="24" height="24" viewBox="0 0 24 24"><path d="M..." fill="currentColor"/></svg>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="footer-bottom">
    <div class="container">
        <div class="footer-bottom__content">
            <p class="footer-copyright">
                © 2025 redrabbit. Всі права захищено.
            </p>
            
            <div class="footer-payments">
                <img src="{% static 'images/payments/visa.svg' %}" alt="Visa" class="payment-logo">
                <img src="{% static 'images/payments/mastercard.svg' %}" alt="Mastercard" class="payment-logo">
                <img src="{% static 'images/payments/googlepay.svg' %}" alt="Google Pay" class="payment-logo">
                <img src="{% static 'images/payments/applepay.svg' %}" alt="Apple Pay" class="payment-logo">
            </div>
        </div>
    </div>
</div>
```

#### 9.2. Оновити footer CSS

**Файл:** `static/css/footer-desktop.css`
**Дія:** Оновити grid та кольори:
```css
.footer-main {
  background: var(--color-text-primary);
  color: var(--color-text-white);
  padding: var(--spacing-xxl) 0;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-xl);
}

.footer-title {
  color: var(--color-text-white);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-md);
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: var(--spacing-sm);
}

.footer-links a {
  color: var(--color-bg-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.footer-links a:hover {
  color: var(--color-brand-light);
}

.footer-schedule {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
}

.footer-schedule__title {
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-xs);
}

.footer-phone a,
.footer-email a {
  color: var(--color-brand-light);
  text-decoration: none;
  font-weight: var(--font-weight-semibold);
}

.footer-social {
  margin-top: var(--spacing-lg);
}

.social-links {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
}

.social-link {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-round);
  color: var(--color-text-white);
  transition: all var(--transition-normal);
}

.social-link:hover {
  background: var(--color-brand-primary);
  transform: translateY(-2px);
}

.footer-bottom {
  background: rgba(0, 0, 0, 0.2);
  padding: var(--spacing-lg) 0;
}

.footer-bottom__content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-payments {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.payment-logo {
  height: 24px;
  width: auto;
  opacity: 0.8;
  transition: opacity var(--transition-fast);
}

.payment-logo:hover {
  opacity: 1;
}

@media (max-width: 992px) {
  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .footer-grid {
    grid-template-columns: 1fr;
  }
  
  .footer-bottom__content {
    flex-direction: column;
    gap: var(--spacing-md);
    text-align: center;
  }
}
```

---

## ⏭️ НАСТУПНІ ФАЗИ (КОРОТКО)

**ФАЗА 10: Сторінка товару** (2-3 дні)
- Галерея з zoom та lightbox
- Табби (Опис, Характеристики, Відгуки, Питання)
- Блок варіантів кольору
- Monobank Частинами інтеграція
- Блоки доставки та оплати

**ФАЗА 11: Фільтри каталогу** (1-2 дні)
- Price range slider
- Checkboxes (бренд, наявність, рейтинг)
- Сортування dropdown
- AJAX фільтрація без перезавантаження
- URL parameters (?price_min=100&brand=womanizer)

**ФАЗА 12: CSS оптимізація** (1 день)
- Об'єднати в 3 бандли: critical.css, main.css, page-specific.css
- Мінімізація
- Видалити дублювання
- Preload критичних ресурсів

**ФАЗА 13: PWA** (1 день)
- manifest.json
- service-worker.js (offline cache)
- Icons 192x192, 512x512

**ФАЗА 14: Tracking** (1 день)
- GTM контейнер
- FB Pixel
- DataLayer events
- Conversion на Thank You Page

**ФАЗА 15: API інтеграції** (3-5 днів)
- Нова Пошта API 2.0
- LiqPay SDK (Apple/Google Pay)
- Monobank Частинами API
- Webhooks

**ФАЗА 16: Тестування та деплой** (2-3 дні)
- PostgreSQL migration
- Redis setup
- Celery workers
- Cloudinary production
- SSL certificates

---

## 📊 ПІДСУМОК ЗМІН

**Нові файли (створити):**
- CSS: age-verification.css, sidebar-menu.css, brands-section.css, reviews-section.css, header-sticky.css
- JS: age-verification.js, live-search.js, reviews-slider.js, sidebar-menu.js
- Templates: includes/sidebar-menu.html, core/brands.html
- Models: ProductReview, Brand (в існуючих файлах)

**Файли для оновлення:**
- static/css/variables.css (кольори redrabbit)
- templates/base.html (meta, links до нових CSS/JS)
- templates/includes/header.html (телефон, live search)
- templates/includes/footer.html (4 колонки, графік, соцмережі)
- templates/core/home.html (sidebar, нові секції)
- apps/core/views.py (brands, reviews в context)
- apps/core/context_processors.py (site_name)
- apps/products/models.py (додати video_url)
- apps/products/admin.py (ProductReview, Brand admin)
- apps/orders/models.py (нові поля)

**Не змінювати (вже працюють):**
- Banner slider
- Cart система
- Wishlist система
- Management commands (import_products, update_prices)
- Існуючі views (CategoryView, ProductDetailView, SearchView)
- Mobile menu та mobile-bottom-nav

---

## 🚨 ВАЖЛИВІ ПРАВИЛА

1. **БЕЗ INLINE СТИЛІВ:** Всі стилі тільки в CSS файлах
2. **БЕЗ !IMPORTANT:** Використовувати специфічність селекторів
3. **БЕЗ INLINE JS:** Всі скрипти в окремих JS файлах
4. **CSS VARIABLES:** Використовувати змінні з variables.css
5. **DEFER/ASYNC:** Всі JS з defer атрибутом
6. **LAZY LOADING:** Всі зображення з loading="lazy"
7. **ARIA LABELS:** Доступність для всіх інтерактивних елементів
8. **SEMANTIC HTML:** Правильні HTML5 теги
9. **RESPONSIVE:** Mobile-first підхід
10. **PERFORMANCE:** Мінімізація, compression, caching

---

**КІНЕЦЬ ПЛАНУ ІМПЛЕМЕНТАЦІЇ**

