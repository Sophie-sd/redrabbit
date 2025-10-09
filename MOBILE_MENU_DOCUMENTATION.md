# Мобільне меню - Повна документація для розробника

## Огляд системи

Система мобільного меню складається з кількох компонентів, які працюють разом для забезпечення повної навігації на мобільних пристроях. Ця система включає:

1. **Головне мобільне меню** (висувне меню збоку)
2. **Нижня мобільна навігація** (фіксована панель знизу)
3. **Мобільний футер** (акордеони та підписка)
4. **Мобільний пошук** (переключення між логотипом і пошуком)

---

## 1. HTML Структура

### 1.1 Головне мобільне меню (`mobile-menu.html`)

**Розташування:** `templates/includes/mobile-menu.html`

```html
<div class="mobile-menu" id="mobile-menu" role="navigation" aria-label="Мобільне меню">
    <!-- Заголовок меню з кнопкою закриття -->
    <div class="mobile-menu-header">
        <button class="mobile-menu-close" id="mobile-menu-close" aria-label="Закрити меню">
            <i class="icon-close" aria-hidden="true"></i>
        </button>
    </div>
    
    <!-- Навігаційна секція -->
    <div class="mobile-menu-nav">
        <!-- Інформація про користувача (авторизований/неавторизований) -->
        {% if user.is_authenticated %}
            <div class="mobile-user-info">
                <div class="user-avatar">
                    <i class="icon-user" aria-hidden="true"></i>
                </div>
                <div class="user-details">
                    <span class="user-name">{{ user.first_name|default:user.username }}</span>
                    {% if user.is_wholesale %}
                        <span class="wholesale-badge">Оптовий клієнт</span>
                    {% else %}
                        <span class="retail-badge">Роздрібний клієнт</span>
                    {% endif %}
                </div>
            </div>
        {% else %}
            <div class="mobile-auth-link">
                <a href="{% url 'users:login' %}" class="mobile-cabinet-btn">
                    <i class="icon-user" aria-hidden="true"></i>
                    Особистий кабінет
                </a>
            </div>
        {% endif %}
        
        <!-- Основне меню навігації -->
        <ul>
            <li><a href="{% url 'core:home' %}">Головна</a></li>
            <li><a href="{% url 'core:catalog' %}">Каталог</a></li>
            
            <!-- Підменю категорій -->
            {% if main_categories %}
                <li class="mobile-submenu">
                    <span class="submenu-title">Категорії</span>
                    <ul class="submenu-list">
                        {% for category in main_categories %}
                            <li><a href="{{ category.get_absolute_url }}">{{ category.name }}</a></li>
                        {% endfor %}
                    </ul>
                </li>
            {% endif %}
            
            <li><a href="{% url 'products:sale' %}">Акції</a></li>
            <li><a href="{% url 'cart:detail' %}">Кошик</a></li>
            <!-- ... інші пункти меню -->
        </ul>
        
        <!-- Дії користувача -->
        <div class="mobile-user-actions">
            <!-- Кнопки в залежності від статусу авторизації -->
        </div>
        
        <!-- Контактна інформація -->
        <div class="mobile-contact-info">
            <div class="contact-item">
                <i class="icon-phone" aria-hidden="true"></i>
                <a href="tel:+380681752654">{{ site_phone }}</a>
            </div>
            <!-- ... інші контакти -->
        </div>
    </div>
</div>
```

**Ключові особливості:**
- Висувається збоку екрана
- Підтримує авторизованих і неавторизованих користувачів
- Має підменю для категорій
- Відображає бейджі для кошика та кількості товарів
- Містить контактну інформацію

### 1.2 Нижня мобільна навігація (`mobile-bottom-nav.html`)

**Розташування:** `templates/includes/mobile-bottom-nav.html`

```html
<nav class="mobile-bottom-nav">
    <a href="{% url 'core:home' %}" class="nav-item {% if request.path == '/' %}active{% endif %}">
        <svg class="nav-icon" viewBox="0 0 24 24">
            <!-- SVG icon -->
        </svg>
        <span class="nav-label">Головна</span>
    </a>
    
    <a href="{% url 'core:catalog' %}" class="nav-item">
        <svg class="nav-icon" viewBox="0 0 24 24">
            <!-- SVG icon -->
        </svg>
        <span class="nav-label">Каталог</span>
    </a>
    
    <a href="{% url 'cart:detail' %}" class="nav-item nav-item-cart">
        <svg class="nav-icon" viewBox="0 0 24 24">
            <!-- SVG icon -->
        </svg>
        <span class="nav-badge" id="mobileCartBadge">0</span>
        <span class="nav-label">Кошик</span>
    </a>
    
    <a href="{% url 'wishlist:list' %}" class="nav-item">
        <svg class="nav-icon" viewBox="0 0 24 24">
            <!-- SVG icon -->
        </svg>
        <span class="nav-badge">{{ wishlist_count }}</span>
        <span class="nav-label">Обране</span>
    </a>
    
    <a href="{% url 'users:login' %}" class="nav-item">
        <svg class="nav-icon" viewBox="0 0 24 24">
            <!-- SVG icon -->
        </svg>
        <span class="nav-label">Профіль</span>
    </a>
</nav>
```

**Ключові особливості:**
- Фіксована позиція знизу екрана
- 5 основних розділів: Головна, Каталог, Кошик, Обране, Профіль
- Динамічні бейджі для кошика та списку бажань
- SVG іконки для кращої якості відображення

### 1.3 Мобільний футер (`mobile-footer.html`)

**Розташування:** `templates/includes/mobile-footer.html`

```html
<div class="mobile-footer">
    <!-- Форма підписки -->
    <div class="mobile-subscribe">
        <p class="mobile-subscribe-title">Першими дізнавайтеся про нові товари та акції</p>
        <form class="subscribe-form" id="mobileSubscribeForm">
            {% csrf_token %}
            <div class="form-group">
                <label for="subscribeName">Ваше ім'я<span class="required">*</span></label>
                <input type="text" id="subscribeName" name="name" class="form-control" required>
            </div>
            <!-- ... інші поля форми -->
        </form>
    </div>
    
    <!-- Соціальні мережі -->
    <div class="mobile-social">
        <a href="https://www.facebook.com/..." class="social-link" target="_blank">
            <svg viewBox="0 0 24 24" fill="currentColor">
                <!-- Facebook icon -->
            </svg>
        </a>
        <!-- ... інші соцмережі -->
    </div>
    
    <!-- Акордеони -->
    <div class="mobile-accordions">
        <div class="accordion-item">
            <button class="accordion-header" onclick="toggleAccordion(this)">
                <span>Сервіси</span>
                <svg class="accordion-icon" viewBox="0 0 24 24">
                    <!-- Chevron icon -->
                </svg>
            </button>
            <div class="accordion-content">
                <ul class="accordion-links">
                    <li><a href="{% url 'core:delivery' %}">Доставка та оплата</a></li>
                    <!-- ... інші посилання -->
                </ul>
            </div>
        </div>
        <!-- ... інші акордеони -->
    </div>
    
    <!-- Копірайт -->
    <div class="mobile-copyright">
        <p class="copyright-text">© Всі права захищені BEAUTY SHOP, 2020-2024</p>
        <p class="developer-link">Розробка сайту <a href="https://www.prometeylabs.com">PrometeyLabs</a></p>
    </div>
</div>

<script>
function toggleAccordion(button) {
    const item = button.parentElement;
    const content = item.querySelector('.accordion-content');
    
    // Закриваємо всі інші акордеони
    document.querySelectorAll('.accordion-item').forEach(otherItem => {
        if (otherItem !== item) {
            otherItem.classList.remove('active');
            otherItem.querySelector('.accordion-content').style.maxHeight = null;
        }
    });
    
    // Перемикаємо поточний акордеон
    item.classList.toggle('active');
    
    if (item.classList.contains('active')) {
        content.style.maxHeight = content.scrollHeight + 'px';
    } else {
        content.style.maxHeight = null;
    }
}
</script>
```

---

## 2. CSS Стилі

### 2.1 Основні стилі мобільного меню

**Файли:**
- `static/css/mobile.min.css` - основні медіа-запити
- `static/css/mobile-app.css` - стилі для мобільних компонентів
- `static/css/components.min.css` - загальні компоненти

### 2.2 Ключові стилі для головного меню

```css
.mobile-menu {
    position: fixed;
    top: 0;
    left: -100%;
    width: 100%;
    max-width: 320px;
    height: 100vh;
    background: white;
    z-index: 1050;
    transition: left 0.3s ease;
    overflow-y: auto;
}

.mobile-menu.active {
    left: 0;
}

.mobile-menu-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1040;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
}

.mobile-menu-overlay.active {
    opacity: 1;
    visibility: visible;
}
```

### 2.3 Стилі нижньої навігації

```css
.mobile-bottom-nav {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    padding: 8px 0 calc(8px + env(safe-area-inset-bottom));
}

@media (max-width: 768px) {
    .mobile-bottom-nav {
        display: flex;
    }
}

.mobile-bottom-nav .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    text-decoration: none;
    color: #999;
    transition: color 0.3s ease;
    position: relative;
    padding: 4px 0;
}

.mobile-bottom-nav .nav-item.active {
    color: #e91e63;
}
```

### 2.4 Медіа-запити

```css
/* Мобільні пристрої (max-width: 767.98px) */
@media (max-width: 767.98px) {
    /* Ховаємо десктопні елементи */
    .top-bar,
    .desktop-actions,
    .main-nav,
    .desktop-nav {
        display: none;
    }
    
    /* Показуємо мобільні елементи */
    .mobile-bottom-nav {
        display: flex;
    }
    
    .mobile-footer {
        display: block;
    }
    
    /* Ховаємо десктопний футер */
    .footer-main,
    .footer-bottom {
        display: none;
    }
}
```

---

## 3. JavaScript Логіка

### 3.1 Основний клас MobileMenu

**Файл:** `static/js/mobile-menu.min.js`

```javascript
class MobileMenu {
    constructor() {
        this.menuBtn = document.getElementById('mobile-menu-btn');
        this.menu = document.getElementById('mobile-menu');
        this.overlay = document.getElementById('mobile-menu-overlay');
        this.closeBtn = document.getElementById('mobile-menu-close');
        this.body = document.body;
        this.isOpen = false;
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.init();
    }

    init() {
        if (!this.menuBtn || !this.menu || !this.overlay) return;
        this.bindEvents();
        this.setupAccessibility();
        this.setupTouchGestures();
    }

    bindEvents() {
        // Відкрити меню
        this.menuBtn.addEventListener('click', e => {
            e.preventDefault();
            this.toggleMenu();
        });

        // Закрити меню
        this.closeBtn.addEventListener('click', e => {
            e.preventDefault();
            this.closeMenu();
        });

        // Закрити меню при кліку на overlay
        this.overlay.addEventListener('click', () => {
            this.closeMenu();
        });

        // Закрити меню при натисканні Escape
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape' && this.isOpen) this.closeMenu();
        });

        // Закрити меню при зміні розміру екрана
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 992 && this.isOpen) this.closeMenu();
        });

        // Закрити меню при переході по посиланню
        const menuLinks = this.menu.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.closeMenu();
            });
        });
    }

    setupTouchGestures() {
        // Підтримка свайпу для закриття меню
        this.menu.addEventListener('touchstart', e => {
            this.touchStartX = e.changedTouches[0].screenX;
        }, {passive: true});

        this.menu.addEventListener('touchend', e => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }, {passive: true});
    }

    handleSwipe() {
        const swipeDistance = this.touchStartX - this.touchEndX;
        const minSwipeDistance = 100;
        
        if (swipeDistance > minSwipeDistance) {
            this.closeMenu();
        }
    }

    openMenu() {
        this.isOpen = true;
        this.menu.classList.add('active');
        this.overlay.classList.add('active');
        this.body.classList.add('menu-open');
        this.menuBtn.setAttribute('aria-expanded', 'true');
        this.menu.setAttribute('aria-hidden', 'false');
        this.menu.focus();
        this.trapFocus();
        this.preventBodyScroll();
    }

    closeMenu() {
        this.isOpen = false;
        this.menu.classList.remove('active');
        this.overlay.classList.remove('active');
        this.body.classList.remove('menu-open');
        this.menuBtn.setAttribute('aria-expanded', 'false');
        this.menu.setAttribute('aria-hidden', 'true');
        this.menuBtn.focus();
        this.allowBodyScroll();
    }

    preventBodyScroll() {
        const scrollY = window.scrollY;
        this.body.style.position = 'fixed';
        this.body.style.top = `-${scrollY}px`;
        this.body.style.width = '100%';
        this.body.dataset.scrollY = scrollY;
    }

    allowBodyScroll() {
        const scrollY = this.body.dataset.scrollY;
        this.body.style.position = '';
        this.body.style.top = '';
        this.body.style.width = '';
        window.scrollTo(0, parseInt(scrollY || '0'));
        delete this.body.dataset.scrollY;
    }
}
```

### 3.2 Клас для підменю

```javascript
class MobileSubmenu {
    constructor() {
        this.submenus = document.querySelectorAll('.mobile-submenu');
        this.init();
    }

    init() {
        this.submenus.forEach(submenu => {
            const title = submenu.querySelector('.submenu-title');
            const list = submenu.querySelector('.submenu-list');
            
            if (title && list) {
                title.addEventListener('click', () => {
                    const isActive = submenu.classList.contains('active');
                    
                    // Закриваємо всі підменю
                    this.submenus.forEach(s => s.classList.remove('active'));
                    
                    // Відкриваємо поточне, якщо воно не було активним
                    if (!isActive) submenu.classList.add('active');
                });
            }
        });
    }
}
```

### 3.3 Мобільний пошук

**Файл:** `static/js/mobile-search.js`

```javascript
(function() {
    'use strict';
    
    let searchToggle, searchForm, searchClose, searchInput, logo, headerContent;
    let isSearchOpen = false;
    
    document.addEventListener('DOMContentLoaded', function() {
        initElements();
        bindEvents();
    });
    
    function initElements() {
        searchToggle = document.getElementById('mobileSearchToggle');
        searchForm = document.getElementById('mobileSearchForm');
        searchClose = document.getElementById('mobileSearchClose');
        searchInput = document.getElementById('mobileSearchInput');
        logo = document.querySelector('.logo');
        headerContent = document.querySelector('.header-content');
        
        return searchToggle && searchForm && searchClose && searchInput && logo;
    }
    
    function bindEvents() {
        if (!initElements()) return;
        
        // Відкрити пошук
        searchToggle.addEventListener('click', openSearch);
        
        // Закрити пошук
        searchClose.addEventListener('click', closeSearch);
        
        // Закрити пошук по ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isSearchOpen) {
                closeSearch();
            }
        });
        
        // Автофокус на поле пошуку
        searchForm.addEventListener('transitionend', function() {
            if (isSearchOpen && searchInput) {
                searchInput.focus();
            }
        });
    }
    
    function openSearch() {
        if (isSearchOpen) return;
        
        isSearchOpen = true;
        
        // Додати класи для анімації
        headerContent.classList.add('search-mode');
        logo.classList.add('logo-hidden');
        searchForm.classList.add('search-form-visible');
        searchToggle.classList.add('search-btn-hidden');
        
        // Фокус на поле вводу
        setTimeout(() => {
            if (searchInput) {
                searchInput.focus();
            }
        }, 300);
    }
    
    function closeSearch() {
        if (!isSearchOpen) return;
        
        isSearchOpen = false;
        
        // Видалити класи для анімації
        headerContent.classList.remove('search-mode');
        logo.classList.remove('logo-hidden');
        searchForm.classList.remove('search-form-visible');
        searchToggle.classList.remove('search-btn-hidden');
        
        // Очистити поле пошуку
        if (searchInput) {
            searchInput.value = '';
            searchInput.blur();
        }
    }
})();
```

---

## 4. Функціональні особливості

### 4.1 Адаптивність

**Брейкпоінти:**
- `max-width: 767.98px` - основний мобільний режим
- `max-width: 575.98px` - маленькі мобільні пристрої
- `max-width: 991.98px` - планшети

### 4.2 Доступність (Accessibility)

- **ARIA атрибути:** `aria-label`, `aria-expanded`, `aria-hidden`
- **Keyboard navigation:** підтримка Tab, Enter, Escape
- **Focus management:** автоматичне керування фокусом при відкритті/закритті
- **Screen reader support:** семантичні HTML теги та ARIA roles

### 4.3 Touch підтримка

- **Swipe gestures:** свайп ліворуч для закриття меню
- **Touch-friendly sizes:** мінімальний розмір кнопок 44px
- **iOS Safari підтримка:** `env(safe-area-inset-bottom)` для iPhone X+

### 4.4 Анімації та переходи

```css
/* Плавні переходи */
.mobile-menu {
    transition: left 0.3s ease;
}

.mobile-menu-overlay {
    transition: all 0.3s ease;
}

.accordion-content {
    transition: max-height 0.3s ease;
}
```

---

## 5. Інтеграція з Django

### 5.1 Context Processors

**Файл:** `apps/core/context_processors.py`

```python
def mobile_menu_context(request):
    """Контекст для мобільного меню"""
    return {
        'main_categories': Category.objects.filter(parent=None)[:8],
        'cart_total_items': get_cart_items_count(request),
        'wishlist_count': get_wishlist_count(request),
        'site_phone': settings.SITE_PHONE,
        'site_email': settings.SITE_EMAIL,
    }
```

### 5.2 Шаблонні теги

**Використання в base.html:**

```html
<!-- Mobile Menu -->
<div class="mobile-menu" id="mobile-menu" role="navigation" aria-label="Мобільне меню">
    {% include 'includes/mobile-menu.html' %}
</div>
<div class="mobile-menu-overlay" id="mobile-menu-overlay"></div>

<!-- Mobile Bottom Navigation -->
{% include 'includes/mobile-bottom-nav.html' %}
```

---

## 6. SEO та Performance

### 6.1 Lazy Loading

- JavaScript файли завантажуються асинхронно
- CSS оптимізований та мінімізований
- SVG іконки вбудовані для швидкого завантаження

### 6.2 SEO оптимізація

- Семантичні HTML теги (`nav`, `header`, `footer`)
- Структуровані дані для мобільної версії
- Правильні meta теги для мобільних пристроїв

---

## 7. Налаштування та кастомізація

### 7.1 Зміна кольорової схеми

```css
:root {
    --primary-pink: #e91e63;
    --primary-dark: #c2185b;
    --neutral-dark: #2c2c2c;
    --white: #ffffff;
}
```

### 7.2 Додавання нових пунктів меню

1. Додати в `mobile-menu.html`:
```html
<li>
    <a href="{% url 'new:page' %}" class="{% if request.resolver_match.url_name == 'page' %}active{% endif %}">
        <i class="icon-new" aria-hidden="true"></i>
        Новий пункт
    </a>
</li>
```

2. Додати стилі в `mobile-app.css`
3. Оновити JavaScript для обробки нових елементів

### 7.3 Налаштування анімацій

```css
/* Швидкість анімацій */
.mobile-menu {
    transition-duration: 0.2s; /* Швидше */
}

/* Тип анімації */
.mobile-menu {
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); /* Material Design */
}
```

---

## 8. Тестування

### 8.1 Мобільні пристрої для тестування

- **iPhone SE (375px)**
- **iPhone 12 (390px)**
- **iPhone 14 Pro Max (430px)**
- **Samsung Galaxy S20 (360px)**
- **iPad Mini (768px)**

### 8.2 Браузери

- Safari iOS
- Chrome Android
- Samsung Internet
- Firefox Mobile

### 8.3 Функціональні тести

1. **Відкриття/закриття меню**
2. **Swipe жести**
3. **Keyboard navigation**
4. **Touch targets (мінімум 44px)**
5. **Scroll behavior**
6. **Performance на слабких пристроях**

---

## 9. Підтримка та обслуговування

### 9.1 Моніторинг помилок

- Console errors у мобільних браузерах
- Touch event conflicts
- iOS Safari специфічні проблеми

### 9.2 Analytics

```javascript
// Трекінг відкриття мобільного меню
this.trackEvent('mobile_menu_open');

// Трекінг кліків по пунктах меню
gtag('event', 'menu_click', {
    event_category: 'Mobile Navigation',
    event_label: linkText
});
```

---

## 10. Майбутні поліпшення

### 10.1 Progressive Web App (PWA)

- Service Worker для кешування
- App-like navigation
- Offline підтримка

### 10.2 Покращення UX

- Haptic feedback на iOS
- Gesture improvements
- Voice search integration
- Dark mode підтримка

### 10.3 Performance

- Virtual scrolling для великих списків
- Intersection Observer для lazy loading
- Web Workers для важких операцій

---

## Висновок

Мобільне меню є критично важливим компонентом для користувацького досвіду на мобільних пристроях. Воно забезпечує:

- **Повну навігацію** по сайту на мобільних пристроях
- **Швидкий доступ** до основних функцій (кошик, пошук, профіль)
- **Адаптивний дизайн** для різних розмірів екранів
- **Accessibility** для користувачів з обмеженими можливостями
- **Performance** оптимізацію для мобільних мереж

Система побудована з урахуванням сучасних стандартів веб-розробки та забезпечує seamless користувацький досвід на всіх мобільних пристроях.
