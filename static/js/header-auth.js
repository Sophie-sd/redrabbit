/**
 * Header Authentication Dropdown
 * БЕЗ jQuery, vanilla JavaScript
 */

(function() {
    'use strict';

    // Ініціалізація після завантаження DOM
    document.addEventListener('DOMContentLoaded', function() {
        initUserDropdown();
    });

    /**
     * Ініціалізація user dropdown меню
     */
    function initUserDropdown() {
        const dropdown = document.querySelector('.user-dropdown');
        
        if (!dropdown) {
            return; // Немає dropdown на сторінці
        }

        const button = dropdown.querySelector('.account-link');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (!button || !menu) {
            return;
        }

        // Toggle dropdown по кліку на кнопку
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isExpanded = button.getAttribute('aria-expanded') === 'true';
            
            if (isExpanded) {
                closeDropdown(button, menu);
            } else {
                openDropdown(button, menu);
            }
        });

        // Закрити dropdown при кліку поза ним
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                closeDropdown(button, menu);
            }
        });

        // Закрити dropdown при натисканні Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeDropdown(button, menu);
            }
        });

        // Закрити dropdown при кліку на пункт меню
        const menuItems = menu.querySelectorAll('.dropdown-item');
        menuItems.forEach(function(item) {
            item.addEventListener('click', function() {
                closeDropdown(button, menu);
            });
        });
    }

    /**
     * Відкрити dropdown меню
     */
    function openDropdown(button, menu) {
        button.setAttribute('aria-expanded', 'true');
        menu.classList.add('dropdown-open');
    }

    /**
     * Закрити dropdown меню
     */
    function closeDropdown(button, menu) {
        button.setAttribute('aria-expanded', 'false');
        menu.classList.remove('dropdown-open');
    }

    // Обробка для мобільних пристроїв
    // Забезпечуємо, що dropdown працює на дотиках
    if ('ontouchstart' in window) {
        document.addEventListener('touchstart', function(e) {
            const dropdown = document.querySelector('.user-dropdown');
            if (!dropdown) {
                return;
            }
            
            const button = dropdown.querySelector('.account-link');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (!button || !menu) {
                return;
            }
            
            // Якщо клікнули не на dropdown, закриваємо його
            if (!dropdown.contains(e.target)) {
                closeDropdown(button, menu);
            }
        });
    }
})();

