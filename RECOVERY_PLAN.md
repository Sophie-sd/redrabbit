# План поетапного відновлення функціоналу

## Етап 1: Створення базових моделей (локально)

```python
# 1. Створити міграцію для нових моделей
python manage.py makemigrations products --name="add_brand_group_purpose_models"

# 2. Застосувати локально для тестування
python manage.py migrate
```

## Етап 2: Додавання зв'язків з Product

```python
# В apps/products/models.py розкоментувати:
class Product(models.Model):
    # ... існуючі поля ...
    
    # Розкоментувати ці поля:
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    product_group = models.ForeignKey(ProductGroup, on_delete=models.SET_NULL, null=True, blank=True)
    purpose = models.ForeignKey(ProductPurpose, on_delete=models.SET_NULL, null=True, blank=True)
```

```bash
# Створити міграцію для нових полів
python manage.py makemigrations products --name="add_product_filter_fields"
```

## Етап 3: Відновлення фільтрів в шаблоні

```html
<!-- В templates/products/category.html розкоментувати: -->
<!-- Фільтр за брендом -->
<div class="filter-section">
    <h4 class="filter-title">Бренд</h4>
    <div class="filter-options" id="brandFilters">
        {% for brand in brands %}
            <label class="filter-checkbox">
                <input type="checkbox" value="{{ brand.slug }}" name="brand">
                <span class="filter-label">{{ brand.name }}</span>
                <span class="filter-count">({{ brand.products_count }})</span>
            </label>
        {% endfor %}
    </div>
</div>
```

## Етап 4: Оновлення views.py

```python
# В apps/products/views.py додати контекст для фільтрів:
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['category'] = self.category
    
    # Додати дані для фільтрів
    context['brands'] = Brand.objects.filter(is_active=True).annotate(
        products_count=Count('product', filter=Q(product__category=self.category))
    ).filter(products_count__gt=0)
    
    context['product_groups'] = ProductGroup.objects.filter(is_active=True).annotate(
        products_count=Count('product', filter=Q(product__category=self.category))
    ).filter(products_count__gt=0)
    
    context['purposes'] = ProductPurpose.objects.filter(is_active=True).annotate(
        products_count=Count('product', filter=Q(product__category=self.category))
    ).filter(products_count__gt=0)
    
    return context
```

## Етап 5: Фінальний деплой

```bash
git add .
git commit -m "✨ Повне відновлення фільтрів: бренди, групи товарів, призначення"
git push origin main
```

## Файли для оновлення:
1. ✅ `apps/products/models.py` - розкоментувати поля
2. ✅ `templates/products/category.html` - розкоментувати фільтри  
3. 🔄 `apps/products/views.py` - додати контекст
4. 🔄 `apps/products/admin.py` - вже готово
5. 🔄 Міграції - створити поетапно
