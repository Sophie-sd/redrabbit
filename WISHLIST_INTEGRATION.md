# 🎯 Wishlist Integration Guide

## Як додати кнопку Wishlist на картки товарів

### 📦 1. Базова кнопка для карток товарів

Додайте цей HTML в шаблон картки товару:

```html
<!-- Wishlist Button -->
<button 
    type="button" 
    class="btn-toggle-wishlist {% if product in wishlist %}active{% endif %}"
    data-product-id="{{ product.id }}"
    aria-label="{% if product in wishlist %}Видалити з обраного{% else %}Додати в обране{% endif %}"
>
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20.84 4.61C20.3292 4.099 19.7228 3.69364 19.0554 3.41708C18.3879 3.14052 17.6725 2.99817 16.95 2.99817C16.2275 2.99817 15.5121 3.14052 14.8446 3.41708C14.1772 3.69364 13.5708 4.099 13.06 4.61L12 5.67L10.94 4.61C9.9083 3.57831 8.50903 2.99871 7.05 2.99871C5.59096 2.99871 4.19169 3.57831 3.16 4.61C2.1283 5.64169 1.54871 7.04097 1.54871 8.5C1.54871 9.95903 2.1283 11.3583 3.16 12.39L4.22 13.45L12 21.23L19.78 13.45L20.84 12.39C21.351 11.8792 21.7564 11.2728 22.0329 10.6054C22.3095 9.93789 22.4518 9.22248 22.4518 8.5C22.4518 7.77752 22.3095 7.06211 22.0329 6.39464C21.7564 5.72718 21.351 5.12084 20.84 4.61Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
</button>
```

### 📍 2. Позиція кнопки на картці

#### Варіант A: В правому верхньому куті (рекомендовано)

```html
<div class="product-card">
    <!-- Wishlist button (absolute position) -->
    <button 
        type="button" 
        class="btn-toggle-wishlist {% if product in wishlist %}active{% endif %}"
        data-product-id="{{ product.id }}"
        style="position: absolute; top: 10px; right: 10px; z-index: 10;"
    >
        <!-- SVG icon -->
    </button>
    
    <!-- Product image -->
    <div class="product-image">
        <img src="{{ product.main_image.url }}" alt="{{ product.name }}">
    </div>
    
    <!-- Product info -->
    <div class="product-info">
        <h3>{{ product.name }}</h3>
        <p class="price">{{ product.price }} ₴</p>
    </div>
</div>
```

#### Варіант B: В футері картки (біля кнопки "В кошик")

```html
<div class="product-card">
    <!-- Product content -->
    
    <!-- Actions footer -->
    <div class="product-actions">
        <button class="btn-toggle-wishlist" data-product-id="{{ product.id }}">
            <svg><!-- heart icon --></svg>
        </button>
        
        <button class="btn-add-to-cart" data-product-id="{{ product.id }}">
            В кошик
        </button>
    </div>
</div>
```

### 🎨 3. CSS стилі для кнопки на картці

```css
/* Wishlist button на картці товару */
.product-card {
    position: relative;
}

.product-card .btn-toggle-wishlist {
    position: absolute;
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    z-index: 10;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Hover effect */
.product-card .btn-toggle-wishlist:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(233, 30, 99, 0.3);
}

/* Active state (в wishlist) */
.product-card .btn-toggle-wishlist.active {
    background: var(--primary-pink);
    animation: heartBeat 0.6s ease;
}

/* Mobile optimization */
@media (max-width: 768px) {
    .product-card .btn-toggle-wishlist {
        width: 36px;
        height: 36px;
        top: 8px;
        right: 8px;
    }
    
    .product-card .btn-toggle-wishlist svg {
        width: 20px;
        height: 20px;
    }
}
```

### ⚡ 4. JavaScript (вже працює автоматично!)

Після додавання кнопки з класом `.btn-toggle-wishlist` та `data-product-id`, 
функціонал працює автоматично завдяки `wishlist.js`:

- ✅ Click toggle (додати/видалити)
- ✅ Анімація серця
- ✅ Оновлення badge counter
- ✅ Toast notification
- ✅ Збереження в session

### 📄 5. Приклад повної картки товару

```html
{% load static %}

<div class="product-card" data-product-id="{{ product.id }}">
    <!-- Wishlist Toggle -->
    <button 
        type="button" 
        class="btn-toggle-wishlist {% if product in wishlist %}active{% endif %}"
        data-product-id="{{ product.id }}"
        aria-label="{% if product in wishlist %}Видалити з обраного{% else %}Додати в обране{% endif %}"
    >
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20.84 4.61C20.3292 4.099 19.7228 3.69364 19.0554 3.41708C18.3879 3.14052 17.6725 2.99817 16.95 2.99817C16.2275 2.99817 15.5121 3.14052 14.8446 3.41708C14.1772 3.69364 13.5708 4.099 13.06 4.61L12 5.67L10.94 4.61C9.9083 3.57831 8.50903 2.99871 7.05 2.99871C5.59096 2.99871 4.19169 3.57831 3.16 4.61C2.1283 5.64169 1.54871 7.04097 1.54871 8.5C1.54871 9.95903 2.1283 11.3583 3.16 12.39L4.22 13.45L12 21.23L19.78 13.45L20.84 12.39C21.351 11.8792 21.7564 11.2728 22.0329 10.6054C22.3095 9.93789 22.4518 9.22248 22.4518 8.5C22.4518 7.77752 22.3095 7.06211 22.0329 6.39464C21.7564 5.72718 21.351 5.12084 20.84 4.61Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </button>

    <!-- Badge (якщо знижка) -->
    {% if product.discount_price %}
    <span class="product-badge sale">Акція</span>
    {% endif %}

    <!-- Image -->
    <a href="{{ product.get_absolute_url }}" class="product-image">
        {% if product.main_image %}
        <img src="{{ product.main_image.url }}" alt="{{ product.name }}" loading="lazy">
        {% else %}
        <div class="no-image">📦</div>
        {% endif %}
    </a>

    <!-- Info -->
    <div class="product-info">
        <h3 class="product-name">
            <a href="{{ product.get_absolute_url }}">{{ product.name }}</a>
        </h3>
        
        {% if product.category %}
        <p class="product-category">{{ product.category.name }}</p>
        {% endif %}

        <div class="product-footer">
            <div class="product-price">
                {% if product.discount_price %}
                <span class="price-old">{{ product.price|floatformat:0 }} ₴</span>
                <span class="price-current">{{ product.discount_price|floatformat:0 }} ₴</span>
                {% else %}
                <span class="price-current">{{ product.price|floatformat:0 }} ₴</span>
                {% endif %}
            </div>

            {% if product.is_available %}
            <button class="btn btn-add-to-cart" data-product-id="{{ product.id }}">
                В кошик
            </button>
            {% else %}
            <span class="out-of-stock">Немає в наявності</span>
            {% endif %}
        </div>
    </div>
</div>
```

### 🔄 6. Перевірка стану wishlist в шаблоні

Щоб перевірити чи товар в wishlist:

```django
{% if product in wishlist %}
    <!-- Товар в wishlist -->
    <button class="btn-toggle-wishlist active" ...>
{% else %}
    <!-- Товар НЕ в wishlist -->
    <button class="btn-toggle-wishlist" ...>
{% endif %}
```

### 📊 7. Wishlist Counter

Counter доступний глобально через context processor:

```django
<!-- В будь-якому шаблоні -->
<span class="wishlist-count">{{ wishlist_count }}</span>

<!-- Або весь wishlist об'єкт -->
<p>У вас {{ wishlist|length }} товарів в обраному</p>
```

### 🎯 8. API Endpoints

#### Додати в wishlist (AJAX)
```javascript
fetch('/wishlist/add/123/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
    }
})
.then(res => res.json())
.then(data => {
    console.log(data.count); // Оновлена кількість
    console.log(data.message); // Повідомлення
});
```

#### Видалити з wishlist (AJAX)
```javascript
fetch('/wishlist/remove/123/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
    }
})
.then(res => res.json())
.then(data => {
    console.log(data.count);
});
```

### ✨ 9. Features

✅ **Session-based** - працює без реєстрації
✅ **Real-time updates** - counter оновлюється миттєво
✅ **AJAX** - без перезавантаження сторінки
✅ **Анімації** - heartBeat при toggle
✅ **Toast notifications** - користувач бачить фідбек
✅ **Mobile optimized** - адаптація для iOS Safari
✅ **Accessibility** - ARIA labels, keyboard navigation

### 🎨 10. Customization

Ви можете змінити стилі кнопки wishlist в `static/css/wishlist.css`:

- `.btn-toggle-wishlist` - базові стилі
- `.btn-toggle-wishlist:hover` - hover effect
- `.btn-toggle-wishlist.active` - active state (в wishlist)
- `.btn-toggle-wishlist.animate-heart` - анімація

### 📱 11. Mobile Bottom Navigation

Wishlist вже інтегровано в mobile navigation:

- Іконка сердечка
- Badge з кількістю
- Active state
- Автоматичне оновлення

### 🚀 12. Готово!

Після додавання кнопки на картки товарів, функціонал працює автоматично:

1. ✅ Click → додає/видаляє з wishlist
2. ✅ Анімація серця
3. ✅ Оновлення counter
4. ✅ Toast notification
5. ✅ Збереження в session

**Без додаткового JavaScript коду!**

