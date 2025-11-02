"""
Розподіляє товари по новим категоріям на основі старих категорій та ключових слів
"""
from django.core.management.base import BaseCommand
from apps.products.models import Category, Product


class Command(BaseCommand):
    help = 'Розподіляє товари по новим категоріям на основі старих'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Маппінг товарів на нові категорії...'))
        
        # Маппінг: ключові слова в назві старої категорії -> slug нової категорії
        mapping_rules = {
            # Для Неї
            'Вібратори': 'for-women-vibratory',
            'Віброкулі': 'for-women-vibrokuli',
            'Кролики': 'for-women-krolyky',
            'We-Vibe': 'for-women-we-vibe',
            'Вакуум': 'for-women-vakuumni',
            'Зона G': 'for-women-zona-g',
            'G-spot': 'for-women-zona-g',
            'Клітор': 'for-women-vaginalno-klitoralni',
            'Фалоімітатор': 'for-women-faloimitatory-vibro',
            'Реалістичн': 'for-women-realistychni',
            'Віброяйц': 'for-women-vibroyaycya',
            'Hi-tech': 'for-women-hi-tech',
            'Пульсатор': 'for-women-pulsatory',
            
            # Для Нього
            'Вагін': 'for-men-vaginy-masturbatory',
            'Мастурбатор': 'for-men-vaginy-masturbatory',
            'Покет': 'for-men-poket-masturbatory',
            'Простат': 'for-men-massage-prostaty',
            'Помп': 'for-men-vakuumni-pompy',
            'Гідропомп': 'for-men-gidropompy',
            'Екстендер': 'for-men-ekstendery',
            
            # Для Пар
            'Страпон': 'for-couples-strapony',
            'Насадк': 'for-couples-nasadky-kilcya',
            'Кільц': 'for-couples-nasadky-kilcya',
            'Смарт': 'for-couples-smart-toys',
            
            # Лубриканти
            'Лубрикант': 'lubricants',
            'Змазк': 'lubricants',
            'Гель': 'lubricants',
            
            # Прелюдія
            'Стимулятор клітор': 'foreplay-stymulator-klitor',
            'Рідкий вібратор': 'foreplay-ridkyy-vibrator',
            'Пролонгатор': 'foreplay-prolongatory',
            'Феромон': 'foreplay-kosmetyka-feromony',
            'Оральн': 'foreplay-oralni-lasky',
            'Стимулятор G': 'foreplay-stymulator-g',
            'Стимулятор пеніс': 'foreplay-stymulator-penis',
            'Свічк': 'foreplay-masazhni-svichky',
            'Масло': 'foreplay-klasychni-masla',
            'Пінк': 'foreplay-masazhni-pinky',
            'Сосків': 'foreplay-stymulator-sosky',
            'Звужу': 'foreplay-zvuzhuyuchi',
            'Гігієн': 'foreplay-intymna-gigiena',
            
            # Білизна
            'Білизн': 'underwear-costumes',
            'Комплект': 'underwear-costumes-komplekty',
            'Боді': 'underwear-costumes-bodi',
            'Корсет': 'underwear-costumes-korsety',
            'Пеньюар': 'underwear-costumes-penyuary-sorochky',
            'Сорочк': 'underwear-costumes-penyuary-sorochky',
            'Бодістокінг': 'underwear-costumes-erotychni-bodystocking',
            'Лаков': 'underwear-costumes-lakovana-bilyzna',
            'Гартер': 'underwear-costumes-gartery-chokery',
            'Чокер': 'underwear-costumes-gartery-chokery',
            'Портупе': 'underwear-costumes-gartery-chokery',
            'Рольов': 'underwear-costumes-rolovi-kostyumy',
            'Костюм': 'underwear-costumes-rolovi-kostyumy',
            
            # BDSM
            'БДСМ': 'bdsm-fetish',
            'BDSM': 'bdsm-fetish',
            'Маск': 'bdsm-fetish-masky-povyazky',
            'Пов\'язк': 'bdsm-fetish-masky-povyazky',
            'Кляп': 'bdsm-fetish-klyapy',
            'Нашийник': 'bdsm-fetish-nashynyky-povidci',
            'Повід': 'bdsm-fetish-nashynyky-povidci',
            'Батіг': 'bdsm-fetish-batogy-steki',
            'Стек': 'bdsm-fetish-batogy-steki',
            'Флогер': 'bdsm-fetish-batogy-steki',
            'Ляскалк': 'bdsm-fetish-batogy-steki',
            'Затискач': 'bdsm-fetish-zatyskachi',
            'Свічк BDSM': 'bdsm-fetish-svichky-bdsm',
            
            # Сексуальне здоров'я
            'Кегел': 'sexual-health-trenazhery-kegelya',
            'Вагінальн кульк': 'sexual-health-vaginalni-kulky',
        }
        
        # Отримуємо всі товари
        products = Product.objects.select_related('primary_category').prefetch_related('categories').all()
        total = products.count()
        updated = 0
        
        self.stdout.write(f'Всього товарів: {total}\n')
        
        for product in products:
            if not product.primary_category:
                continue
                
            old_category_name = product.primary_category.name
            matched = False
            
            # Шукаємо відповідність по ключовим словам
            for keyword, new_slug in mapping_rules.items():
                if keyword.lower() in old_category_name.lower():
                    try:
                        new_category = Category.objects.get(slug=new_slug)
                        
                        # Додаємо до ManyToMany categories якщо ще не додано
                        if not product.categories.filter(id=new_category.id).exists():
                            product.categories.add(new_category)
                            updated += 1
                            matched = True
                            
                            if updated % 100 == 0:
                                self.stdout.write(f'  Оброблено: {updated} товарів...')
                        
                        break  # Знайшли відповідність, виходимо
                        
                    except Category.DoesNotExist:
                        continue
            
            # Якщо не знайшли відповідність, додаємо до загальної категорії
            if not matched and not product.categories.exists():
                # Визначаємо загальну категорію за типом
                if 'вібратор' in old_category_name.lower() or 'для жінок' in old_category_name.lower():
                    try:
                        general_cat = Category.objects.get(slug='for-women')
                        product.categories.add(general_cat)
                        updated += 1
                    except Category.DoesNotExist:
                        pass
                        
                elif 'для чоловік' in old_category_name.lower() or 'мастурбатор' in old_category_name.lower():
                    try:
                        general_cat = Category.objects.get(slug='for-men')
                        product.categories.add(general_cat)
                        updated += 1
                    except Category.DoesNotExist:
                        pass
                        
                elif 'для пар' in old_category_name.lower():
                    try:
                        general_cat = Category.objects.get(slug='for-couples')
                        product.categories.add(general_cat)
                        updated += 1
                    except Category.DoesNotExist:
                        pass
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Завершено!'))
        self.stdout.write(f'  Оновлено товарів: {updated}')
