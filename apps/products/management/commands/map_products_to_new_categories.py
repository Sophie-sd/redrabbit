"""
Маппить товари зі старих категорій постачальника на нові категорії
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from apps.products.models import Category, Product


class Command(BaseCommand):
    help = 'Розподіляє товари по новим категоріям на основі старих'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Маппінг товарів на нові категорії...'))
        
        # Маппінг: старий slug -> нові slugs (можна кілька категорій)
        # Формат: {'старий-slug': ['новий-slug-1', 'новий-slug-2']}
        CATEGORY_MAPPING = {
            # Жінкам - Вібратори
            'vibrators': ['zinkam-vibratori', 'seks-igraski-vibratori'],
            'rabbits': ['zinkam-kroliki'],
            'clitoral-vibrators': ['zinkam-vibratori', 'seks-igraski-vibratori'],
            'g-spot': ['zinkam-zona-g'],
            
            # Чоловікам
            'masturbators': ['colovikam-vagini-realisticni-masturbatori', 'seks-igraski-masturbatori-i-vagini'],
            'prostate-massagers': ['colovikam-masazeri-prostati-z-vibracieu', 'seksualne-zdorovya-masazeri-prostati'],
            'pumps': ['colovikam-vakuumni-pompi', 'seksualne-zdorovya-vakuumni-pompi-gidropompi'],
            
            # Для пар
            'couple-toys': ['dla-dvox-vibratori', 'dla-dvox-na-podarunok'],
            'strap-ons': ['dla-dvox-straponi', 'seks-igraski-straponi'],
            
            # Білизна
            'lingerie': ['bilizna-kostumi-komplekti'],
            'costumes': ['bilizna-kostumi-rolovi-kostumi'],
            'bodystockings': ['bilizna-kostumi-eroticni-bodistokinci-i-kostumi-sitka'],
            
            # БДСМ
            'bdsm': ['bdsm-fetis-nabori-igrasok'],
            'restraints': ['bdsm-fetis-nasijniki-povidci'],
            'whips': ['bdsm-fetis-batogi-steki-flogeri-laskalni'],
            
            # Лубриканти
            'lubricants-water': ['lubrikanti-vagina гні'],
            'lubricants-silicone': ['lubrikanti-analni'],
            'lubricants-anal': ['lubrikanti-analni'],
            'lubricants-oral': ['lubrikanti-oralni-istivni'],
            
            # Прелюдія
            'massage-oils': ['preludia-klasicni-masla-na-maslianij-osnovi'],
            'massage-candles': ['preludia-masazni-svicki'],
            'arousal-gels': ['preludia-ridkij-vibrator'],
            
            # Сексуальне здоров'я
            'kegel': ['seksualne-zdorovya-trenazeri-kegelia'],
            'penis-pumps': ['seksualne-zdorovya-vakuumni-pompi-gidropompi'],
            'extenders': ['seksualne-zdorovya-ekstenderi-zbilsenna-clena'],
        }
        
        # Кеш категорій
        categories_cache = {cat.slug: cat for cat in Category.objects.all()}
        
        updated_count = 0
        error_count = 0
        
        # Обробляємо всі товари
        products = Product.objects.all().prefetch_related('categories')
        total = products.count()
        
        self.stdout.write(f'Всього товарів: {total}')
        
        for idx, product in enumerate(products, 1):
            try:
                # Спробуємо знайти primary_category товару
                old_primary = product.primary_category
                
                if not old_primary or not old_primary.slug:
                    continue
                
                old_slug = old_primary.slug
                
                # Шукаємо маппінг для старої категорії
                new_slugs = CATEGORY_MAPPING.get(old_slug, [])
                
                # Якщо немає точного маппінгу, пробуємо по ключових словах
                if not new_slugs:
                    new_slugs = self._find_by_keywords(old_slug, old_primary.name)
                
                if new_slugs:
                    # Додаємо товар до нових категорій
                    new_categories = []
                    for new_slug in new_slugs:
                        if new_slug in categories_cache:
                            new_categories.append(categories_cache[new_slug])
                    
                    if new_categories:
                        # Очищаємо старі категорії
                        product.categories.clear()
                        
                        # Додаємо нові
                        product.categories.add(*new_categories)
                        
                        # Встановлюємо primary_category (перша, найбільш спільна)
                        product.primary_category = new_categories[0]
                        product.save(update_fields=['primary_category'])
                        
                        updated_count += 1
                        
                        if idx % 100 == 0:
                            self.stdout.write(f'  Оброблено: {idx}/{total}')
            
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'  Помилка для товару {product.id}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Завершено!'))
        self.stdout.write(f'  Оновлено товарів: {updated_count}')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  Помилок: {error_count}'))
    
    def _find_by_keywords(self, old_slug, old_name):
        """Пошук нових категорій по ключових словах"""
        keywords_map = {
            'vibr': ['zinkam-vibratori'],
            'rabbit': ['zinkam-kroliki'],
            'masturb': ['colovikam-vagini-realisticni-masturbatori'],
            'prostat': ['colovikam-masazeri-prostati-z-vibracieu'],
            'pump': ['colovikam-vakuumni-pompi'],
            'strap': ['dla-dvox-straponi'],
            'lingerie': ['bilizna-kostumi-komplekti'],
            'costume': ['bilizna-kostumi-rolovi-kostumi'],
            'bdsm': ['bdsm-fetis-nabori-igrasok'],
            'lubric': ['lubrikanti-vaginalni'],
            'massage': ['preludia-klasicni-masla-na-maslianij-osnovi'],
            'kegel': ['seksualne-zdorovya-trenazeri-kegelia'],
        }
        
        old_text = f"{old_slug} {old_name}".lower()
        
        for keyword, slugs in keywords_map.items():
            if keyword in old_text:
                return slugs
        
        return []

