/**
 * Sidebar Menu - Click-based accordion menu
 * Відкриття/закриття підменю по кліку
 */
(function() {
    'use strict';
    
    const menuItems = document.querySelectorAll('.sidebar-menu__item.has-children');
    
    menuItems.forEach(item => {
        const link = item.querySelector('.sidebar-menu__link');
        const submenu = item.querySelector('.sidebar-menu__submenu');
        const arrow = item.querySelector('.sidebar-menu__arrow');
        
        if (!link || !submenu) return;
        
        // Click handler для головної категорії
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isOpen = item.classList.contains('menu-open');
            
            // Закриваємо всі інші підменю
            menuItems.forEach(otherItem => {
                if (otherItem !== item) {
                    closeSubmenu(otherItem);
                }
            });
            
            // Перемикаємо поточне підменю
            if (isOpen) {
                closeSubmenu(item);
            } else {
                openSubmenu(item);
            }
        });
        
        // Дозволяємо клік по підкатегоріях (перехід на сторінку)
        const subLinks = submenu.querySelectorAll('.submenu__link');
        subLinks.forEach(subLink => {
            subLink.addEventListener('click', function(e) {
                e.stopPropagation();
                // Дозволяємо перехід
            });
        });
    });
    
    // Відкриваємо активну категорію при завантаженні сторінки
    const activeItem = document.querySelector('.sidebar-menu__item.active.has-children');
    if (activeItem && !activeItem.classList.contains('info-menu')) {
        openSubmenu(activeItem);
    }
    
    // Закриваємо всі підменю при кліку поза меню
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.sidebar-menu')) {
            menuItems.forEach(item => {
                closeSubmenu(item);
            });
        }
    });
    
    /**
     * Відкриває підменю
     */
    function openSubmenu(item) {
        const submenu = item.querySelector('.sidebar-menu__submenu');
        const arrow = item.querySelector('.sidebar-menu__arrow');
        
        if (!submenu) return;
        
        item.classList.add('menu-open');
        submenu.style.maxHeight = submenu.scrollHeight + 'px';
        
        if (arrow) {
            arrow.style.transform = 'rotate(90deg)';
        }
    }
    
    /**
     * Закриває підменю
     */
    function closeSubmenu(item) {
        const submenu = item.querySelector('.sidebar-menu__submenu');
        const arrow = item.querySelector('.sidebar-menu__arrow');
        
        if (!submenu) return;
        
        item.classList.remove('menu-open');
        submenu.style.maxHeight = '0';
        
        if (arrow) {
            arrow.style.transform = 'rotate(0deg)';
        }
    }
    
    // Оновлюємо max-height при зміні розміру вікна
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            menuItems.forEach(item => {
                if (item.classList.contains('menu-open')) {
                    const submenu = item.querySelector('.sidebar-menu__submenu');
                    if (submenu) {
                        submenu.style.maxHeight = submenu.scrollHeight + 'px';
                    }
                }
            });
        }, 250);
    });
    
})();
