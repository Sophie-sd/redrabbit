/**
 * Мобільний пошук - функціонал переключення логотип/пошук
 */
(function() {
    'use strict';
    
    // Елементи DOM
    let searchToggle, searchForm, searchClose, searchInput, logo, headerContent;
    let isSearchOpen = false;
    
    // Ініціалізація при завантаженні DOM
    document.addEventListener('DOMContentLoaded', function() {
        initElements();
        bindEvents();
    });
    
    /**
     * Ініціалізація елементів
     */
    function initElements() {
        searchToggle = document.getElementById('mobileSearchToggle');
        searchForm = document.getElementById('mobileSearchForm');
        searchClose = document.getElementById('mobileSearchClose');
        searchInput = document.getElementById('mobileSearchInput');
        logo = document.querySelector('.logo');
        headerContent = document.querySelector('.header-content');
        
        // Перевірка наявності всіх необхідних елементів
        if (!searchToggle || !searchForm || !searchClose || !searchInput || !logo) {
            console.warn('Mobile search: Not all required elements found');
            return false;
        }
        
        return true;
    }
    
    /**
     * Прив'язка подій
     */
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
        
        // Закрити пошук при кліку поза формою (тільки на мобільних)
        document.addEventListener('click', function(e) {
            if (isSearchOpen && 
                window.innerWidth <= 768 && 
                !searchForm.contains(e.target) && 
                !searchToggle.contains(e.target)) {
                closeSearch();
            }
        });
        
        // Автофокус на поле пошуку при відкритті
        searchForm.addEventListener('transitionend', function() {
            if (isSearchOpen && searchInput) {
                searchInput.focus();
            }
        });
        
        // Обробка подання форми
        searchForm.querySelector('.mobile-search-form').addEventListener('submit', function(e) {
            const query = searchInput.value.trim();
            if (!query) {
                e.preventDefault();
                searchInput.focus();
                return false;
            }
        });
    }
    
    /**
     * Відкрити пошук
     */
    function openSearch() {
        if (isSearchOpen) return;
        
        isSearchOpen = true;
        
        // Додати класи для анімації
        headerContent.classList.add('search-mode');
        logo.classList.add('logo-hidden');
        searchForm.classList.add('search-form-visible');
        searchToggle.classList.add('search-btn-hidden');
        
        // Атрибути доступності
        searchToggle.setAttribute('aria-expanded', 'true');
        searchForm.setAttribute('aria-hidden', 'false');
        
        // Фокус на поле вводу з невеликою затримкою для анімації
        setTimeout(() => {
            if (searchInput) {
                searchInput.focus();
            }
        }, 300);
    }
    
    /**
     * Закрити пошук
     */
    function closeSearch() {
        if (!isSearchOpen) return;
        
        isSearchOpen = false;
        
        // Видалити класи для анімації
        headerContent.classList.remove('search-mode');
        logo.classList.remove('logo-hidden');
        searchForm.classList.remove('search-form-visible');
        searchToggle.classList.remove('search-btn-hidden');
        
        // Атрибути доступності
        searchToggle.setAttribute('aria-expanded', 'false');
        searchForm.setAttribute('aria-hidden', 'true');
        
        // Очистити поле пошуку
        if (searchInput) {
            searchInput.value = '';
            searchInput.blur();
        }
    }
    
    /**
     * Обробка зміни розміру екрану
     */
    window.addEventListener('resize', function() {
        // Закрити пошук на десктопі
        if (window.innerWidth > 768 && isSearchOpen) {
            closeSearch();
        }
    });
    
    // Експорт функцій для глобального доступу (якщо потрібно)
    window.MobileSearch = {
        open: openSearch,
        close: closeSearch,
        toggle: function() {
            isSearchOpen ? closeSearch() : openSearch();
        },
        isOpen: function() {
            return isSearchOpen;
        }
    };
})();
