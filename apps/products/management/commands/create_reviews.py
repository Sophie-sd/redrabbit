from django.core.management.base import BaseCommand
from apps.products.models import Product, ProductReview, Category
from datetime import datetime, timedelta
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Створює тестові відгуки для товарів'

    def handle(self, *args, **options):
        reviews_data = [
            {
                'author_name': 'Ірина',
                'rating': 5,
                'text': 'Замовила цей стимулятор після довгих роздумів і не пошкодувала! Якість на висоті, робота безшумна, ефект вражає. Доставка швидка, упаковка дискретна.',
                'category_badge': 'Стимулятори',
                'product_name': 'Satisfyer'
            },
            {
                'author_name': 'Наталія',
                'rating': 5,
                'text': 'Це моя перша покупка такого типу і я в захваті! Дуже делікатна доставка, гарна упаковка. Сам товар перевершив очікування, тепер розумію що витрачала час марно раніше 😊',
                'category_badge': 'Вібратори',
                'product_name': 'Вібратор'
            },
            {
                'author_name': 'Дмитро',
                'rating': 4,
                'text': 'Купив цей мастурбатор для себе, матеріал якісний, відчуття реалістичні. Єдиний мінус - трохи гучніше працює ніж очікував. В цілому задоволений покупкою.',
                'category_badge': 'Мастурбатори',
                'product_name': 'Мастурбатор'
            },
            {
                'author_name': 'Олена',
                'rating': 5,
                'text': 'Чудовий вібратор! Компактний, потужний, ідеально підходить для початківців. Дуже задоволена покупкою, рекомендую всім подругам!',
                'category_badge': 'Вібратори',
                'product_name': 'Вібратор'
            },
            {
                'author_name': 'Катерина',
                'rating': 5,
                'text': 'Давно хотіла спробувати вакуумний стимулятор і не прогадала! Дуже приємні відчуття, робота безшумна. Упаковка дискретна, все прийшло швидко. Дякую магазину!',
                'category_badge': 'Вакуумні стимулятори',
                'product_name': 'Satisfyer'
            },
            {
                'author_name': 'Андрій',
                'rating': 5,
                'text': 'Взяли це кільце з дружиною, щоб додати різноманітності. Відмінна якість, зручне у використанні, всім рекомендую!',
                'category_badge': 'Ерекційні кільця',
                'product_name': 'кільце'
            },
            {
                'author_name': 'Марія',
                'rating': 4,
                'text': 'Вибрала цей стимулятор за відгуками і не пошкодувала. Якість хороша, ефект є. Мінус тільки один - хотілося б більше режимів.',
                'category_badge': 'Стимулятори',
                'product_name': 'стимулятор'
            },
            {
                'author_name': 'Світлана',
                'rating': 5,
                'text': 'Брала як подарунок подрузі на день народження, вона в захваті! Матеріал приємний, все працює ідеально. Дякую за швидку доставку та дискретну упаковку!',
                'category_badge': 'Вібратори',
                'product_name': 'Вібратор'
            }
        ]

        active_products = list(Product.objects.filter(is_active=True))
        
        if not active_products:
            self.stdout.write(self.style.WARNING('Немає активних товарів. Створюю товари-заглушки...'))
            
            category = Category.objects.filter(is_active=True).first()
            if not category:
                category = Category.objects.create(
                    name='Для неї',
                    slug='for-her',
                    is_active=True,
                    sort_order=1
                )
            
            for review_data in reviews_data:
                product = Product.objects.create(
                    name=review_data['product_name'],
                    slug=f"product-{random.randint(1000, 9999)}",
                    primary_category=category,
                    retail_price=999,
                    is_active=True,
                    description=f"Товар категорії {review_data['category_badge']}"
                )
                active_products.append(product)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Створено {len(active_products)} товарів'))

        ProductReview.objects.filter(is_approved=True).delete()
        created_count = 0
        
        review_dates = [
            datetime(2025, 1, 15),
            datetime(2025, 2, 3),
            datetime(2025, 2, 28),
            datetime(2025, 3, 10),
            datetime(2025, 4, 5),
            datetime(2025, 5, 18),
            datetime(2025, 6, 22),
            datetime(2025, 7, 8),
        ]

        for idx, review_data in enumerate(reviews_data):
            product = Product.objects.filter(
                name__icontains=review_data['product_name'].split()[0],
                is_active=True
            ).first()
            
            if not product:
                product = random.choice(active_products)
            
            review = ProductReview.objects.create(
                product=product,
                author_name=review_data['author_name'],
                rating=review_data['rating'],
                text=review_data['text'],
                category_badge=review_data['category_badge'],
                is_approved=True
            )
            
            review.created_at = timezone.make_aware(review_dates[idx])
            review.save(update_fields=['created_at'])
            
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'✓ Створено {created_count} відгуків')
        )

