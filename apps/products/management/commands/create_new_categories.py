"""
Створює нову структуру категорій згідно нової схеми
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Category


class Command(BaseCommand):
    help = 'Створює нову структуру категорій'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Створення нової структури категорій...'))
        
        # Структура категорій з іконками та типами
        categories_structure = [
            {
                'name': 'Для Неї',
                'slug': 'for-women',
                'icon': '♀',
                'type': 'women',
                'children': [
                    ('Вібратори', 'vibratory'),
                    ('Віброкулі', 'vibrokuli'),
                    ('Кролики', 'krolyky'),
                    ('Для пар (We-Vibe)', 'we-vibe'),
                    ('Вакуумні', 'vakuumni'),
                    ('Зона G', 'zona-g'),
                    ('Вагінально-кліторальні', 'vaginalno-klitoralni'),
                    ('Фалоімітатори з вібрацією', 'faloimitatory-vibro'),
                    ('Реалістичні', 'realistychni'),
                    ('Віброяйця', 'vibroyaycya'),
                    ('Hi-tech іграшки', 'hi-tech'),
                    ('Пульсатори', 'pulsatory'),
                ]
            },
            {
                'name': 'Для Нього',
                'slug': 'for-men',
                'icon': '♂',
                'type': 'men',
                'children': [
                    ('Вагіни (реалістичні мастурбатори)', 'vaginy-masturbatory'),
                    ('Покет-мастурбатори', 'poket-masturbatory'),
                    ('З вібрацією і Hi-Tech', 'vibro-hitech'),
                    ('Масажери простати з вібрацією', 'massage-prostaty'),
                    ('Вакуумні помпи', 'vakuumni-pompy'),
                    ('Гідропомпи', 'gidropompy'),
                    ('Екстендери', 'ekstendery'),
                ]
            },
            {
                'name': 'Для Пар',
                'slug': 'for-couples',
                'icon': '💑',
                'type': 'couple',
                'children': [
                    ('Вібратори', 'vibratory-couple'),
                    ('Страпони', 'strapony'),
                    ('Насадки та ерекційні кільця', 'nasadky-kilcya'),
                    ('Смарт-іграшки', 'smart-toys'),
                ]
            },
            {
                'name': 'Лубриканти',
                'slug': 'lubricants',
                'icon': '🧴',
                'type': 'general',
                'children': [
                    ('На водній основі', 'na-vodniy-osnovi'),
                    ('На силіконовій основі', 'na-silikonoviy-osnovi'),
                    ('Для анального сексу і фістинга', 'analnyy-fisting'),
                    ('Смакові (оральні)', 'smakovi-oralni'),
                    ('Збуджуючі і стимулюючі', 'zbudzhuyuchi'),
                    ('Для Іграшок', 'dlya-igrashok'),
                    ('На комбінованій основі', 'kombinovani'),
                ]
            },
            {
                'name': 'Прелюдія',
                'slug': 'foreplay',
                'icon': '📅',
                'type': 'general',
                'children': [
                    ('Стимулятори для клітора', 'stymulator-klitor'),
                    ('Рідкий вібратор', 'ridkyy-vibrator'),
                    ('Пролонгатори для чоловіків', 'prolongatory'),
                    ('Косметика з феромонами', 'kosmetyka-feromony'),
                    ('Засоби для оральних ласк', 'oralni-lasky'),
                    ('Стимулятори для точки G', 'stymulator-g'),
                    ('Стимулятори для пеніса', 'stymulator-penis'),
                    ('Масажні свічки', 'masazhni-svichky'),
                    ('Класичні масла на масляній основі', 'klasychni-masla'),
                    ('Масажні пінки', 'masazhni-pinky'),
                    ('Стимулятори для сосків', 'stymulator-sosky'),
                    ('Звужуючі засоби', 'zvuzhuyuchi'),
                    ('Для інтимної гігієни', 'intymna-gigiena'),
                ]
            },
            {
                'name': 'Білизна-Костюми',
                'slug': 'underwear-costumes',
                'icon': '👙',
                'type': 'general',
                'children': [
                    ('Комплекти', 'komplekty'),
                    ('Боді', 'bodi'),
                    ('Корсети', 'korsety'),
                    ('Пеньюари і сорочки', 'penyuary-sorochky'),
                    ('Еротичні бодістокінги і костюми-сітка', 'erotychni-bodystocking'),
                    ('Лакована білизна', 'lakovana-bilyzna'),
                    ('Гартери, чокери, портупеї', 'gartery-chokery'),
                    ('Рольові костюми', 'rolovi-kostyumy'),
                ]
            },
            {
                'name': 'BDSM',
                'slug': 'bdsm-fetish',
                'icon': '🔗',
                'type': 'general',
                'children': [
                    ('Набори іграшок', 'nabory-igrashok'),
                    ('Маски, пов\'язки', 'masky-povyazky'),
                    ('Кляпи', 'klyapy'),
                    ('Нашийники, повідці', 'nashynyky-povidci'),
                    ('Батоги, стеки, флогери, ляскалки', 'batogy-steki'),
                    ('Затискачі для сосків та грудей', 'zatyskachi'),
                    ('Свічки для BDSM', 'svichky-bdsm'),
                ]
            },
            {
                'name': 'Сексуальне здоров\'я',
                'slug': 'sexual-health',
                'icon': '🩺',
                'type': 'general',
                'children': [
                    ('Масажери простати', 'masazhery-prostaty'),
                    ('Тренажери Кегеля', 'trenazhery-kegelya'),
                    ('Екстендери (збільшення члена)', 'ekstendery-health'),
                    ('Вакуумні помпи, гідропомпи', 'pompy-gidropompy'),
                    ('Вагінальні кульки', 'vaginalni-kulky'),
                ]
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for cat_data in categories_structure:
            # Створюємо головну категорію
            parent_slug = cat_data['slug']
            parent, created = Category.objects.get_or_create(
                slug=parent_slug,
                defaults={
                    'name': cat_data['name'],
                    'icon': cat_data['icon'],
                    'category_type': cat_data['type'],
                    'is_active': True,
                    'sort_order': created_count,
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Створено: {parent.name} ({parent.icon})')
                created_count += 1
            else:
                # Оновлюємо іконку та тип
                parent.icon = cat_data['icon']
                parent.category_type = cat_data['type']
                parent.name = cat_data['name']
                parent.save()
                self.stdout.write(f'  ↻ Оновлено: {parent.name}')
                updated_count += 1
            
            # Створюємо підкатегорії
            for idx, child_data in enumerate(cat_data.get('children', [])):
                if isinstance(child_data, tuple):
                    child_name, child_slug_suffix = child_data
                else:
                    child_name = child_data
                    child_slug_suffix = slugify(child_name)
                
                child_slug = f"{parent_slug}-{child_slug_suffix}"
                child, child_created = Category.objects.get_or_create(
                    slug=child_slug,
                    defaults={
                        'name': child_name,
                        'parent': parent,
                        'is_active': True,
                        'sort_order': idx,
                        'category_type': cat_data['type'],
                    }
                )
                
                if child_created:
                    self.stdout.write(f'    ✓ Підкатегорія: {child.name}')
                    created_count += 1
                else:
                    child.name = child_name
                    child.parent = parent
                    child.save()
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Завершено! Створено: {created_count}, оновлено: {updated_count}'))
