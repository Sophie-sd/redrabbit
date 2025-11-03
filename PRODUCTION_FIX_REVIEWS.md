# Інструкція: Виправлення відгуків на Production

## Проблема
Таблиця `products_productreview` створена без поля `product_id`, що унеможливлює створення відгуків.

## Рішення для Production (PostgreSQL)

### Крок 1: Оновити код
```bash
git pull origin main
```

### Крок 2: Додати поле product_id до таблиці
```bash
python manage.py dbshell
```

У консолі PostgreSQL виконайте:
```sql
-- Додати поле product_id
ALTER TABLE products_productreview 
ADD COLUMN IF NOT EXISTS product_id BIGINT 
REFERENCES products_product(id) ON DELETE CASCADE;

-- Створити індекси
CREATE INDEX IF NOT EXISTS products_pr_product_160d92_idx 
ON products_productreview (product_id, is_approved);

CREATE INDEX IF NOT EXISTS products_pr_is_appr_b55fbf_idx 
ON products_productreview (is_approved, created_at DESC);

-- Вийти
\q
```

### Крок 3: Застосувати міграції
```bash
python manage.py migrate products 0027 --fake
python manage.py migrate products 0028 --fake
python manage.py migrate
```

### Крок 4: Створити відгуки
```bash
python manage.py create_reviews
```

### Крок 5: Перевірити
Відкрийте головну сторінку сайту - внизу має відображатися секція "Відгуки користувачів" з 8 відгуками.

## Перевірка результату
```bash
python manage.py shell -c "from apps.products.models import ProductReview; print('Відгуків:', ProductReview.objects.filter(is_approved=True).count())"
```

Має вивести: `Відгуків: 8`

## Якщо щось пішло не так
Видаліть всі відгуки і створіть заново:
```bash
python manage.py shell -c "from apps.products.models import ProductReview; ProductReview.objects.all().delete()"
python manage.py create_reviews
```

