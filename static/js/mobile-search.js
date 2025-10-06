/**
 * Mobile Search Functionality
 * Відповідає за роботу мобільного пошуку - показ/приховування поля пошуку
 */

class MobileSearch {
    constructor() {
        this.searchToggle = document.getElementById('mobileSearchToggle');
        this.searchContainer = document.getElementById('mobileSearchContainer');
        this.searchInput = document.getElementById('mobileSearchInput');
        this.searchClose = document.getElementById('mobileSearchClose');
        this.header = document.querySelector('.main-header');
        
        this.isActive = false;
        
        this.init();
    }
    
    init() {
        if (!this.searchToggle || !this.searchContainer) {
            return;
        }
        
        // Обробники подій
        this.searchToggle.addEventListener('click', () => this.toggleSearch());
        
        if (this.searchClose) {
            this.searchClose.addEventListener('click', () => this.closeSearch());
        }
        
        // Закриття при натисканні Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isActive) {
                this.closeSearch();
            }
        });
        
        // Закриття при натисканні поза областю пошуку
        document.addEventListener('click', (e) => {
            if (this.isActive && 
                !this.searchContainer.contains(e.target) && 
                !this.searchToggle.contains(e.target)) {
                this.closeSearch();
            }
        });
        
        // Запобігання закриття при кліку всередині контейнера пошуку
        this.searchContainer?.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
    
    toggleSearch() {
        if (this.isActive) {
            this.closeSearch();
        } else {
            this.openSearch();
        }
    }
    
    openSearch() {
        if (!this.searchContainer) return;
        
        this.isActive = true;
        
        // Додати клас активності
        this.searchContainer.classList.add('active');
        this.header?.classList.add('mobile-search-active');
        
        // Затримка для анімації, потім фокус на поле
        setTimeout(() => {
            if (this.searchInput) {
                this.searchInput.focus();
            }
        }, 300);
        
        // Запобігання прокручування сторінки
        document.body.style.overflow = 'hidden';
        
        // Додати ARIA атрибути для доступності
        this.searchToggle?.setAttribute('aria-expanded', 'true');
        this.searchContainer?.setAttribute('aria-hidden', 'false');
    }
    
    closeSearch() {
        if (!this.searchContainer) return;
        
        this.isActive = false;
        
        // Прибрати клас активності
        this.searchContainer.classList.remove('active');
        this.header?.classList.remove('mobile-search-active');
        
        // Очистити поле пошуку при закритті (опціонально)
        // if (this.searchInput) {
        //     this.searchInput.value = '';
        // }
        
        // Відновити прокручування сторінки
        document.body.style.overflow = '';
        
        // Оновити ARIA атрибути
        this.searchToggle?.setAttribute('aria-expanded', 'false');
        this.searchContainer?.setAttribute('aria-hidden', 'true');
    }
    
    // Метод для програматичного відкриття пошуку (може бути корисний)
    focus() {
        this.openSearch();
    }
}

// Ініціалізація після завантаження DOM
document.addEventListener('DOMContentLoaded', () => {
    // Перевірка, чи це мобільний пристрій
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        window.mobileSearch = new MobileSearch();
    }
    
    // Переініціалізація при зміні розміру вікна
    window.addEventListener('resize', () => {
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile && !window.mobileSearch) {
            window.mobileSearch = new MobileSearch();
        } else if (!isMobile && window.mobileSearch) {
            // Закрити пошук при переключенні на десктоп
            window.mobileSearch.closeSearch();
        }
    });
});

// Експорт для можливого використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileSearch;
}
