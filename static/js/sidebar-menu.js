/**
 * Sidebar Menu - Click-based accordion menu
 * Відкриття/закриття підменю по кліку
 * Працює на всіх пристроях включно з iOS Safari
 */
(function() {
    'use strict';
    
    // Чекаємо поки DOM повністю завантажиться
    function initSidebarMenu() {
        const menuItems = document.querySelectorAll('.sidebar-menu__item.has-children');
        
        if (!menuItems || menuItems.length === 0) {
            console.log('Sidebar menu items not found');
            return;
        }
        
        console.log('Sidebar menu initialized with', menuItems.length, 'items');
        
        // Змінна для відстеження подій (уникнення дублювання)
        let eventHandled = false;
        
        menuItems.forEach((item, index) => {
            const link = item.querySelector('.sidebar-menu__link');
            const submenu = item.querySelector('.sidebar-menu__submenu');
            const arrow = item.querySelector('.sidebar-menu__arrow');
            
            if (!link || !submenu) {
                console.log('Missing link or submenu for item', index);
                return;
            }
            
            // Функція обробки кліку/тапу
            function handleToggle(e) {
                // Якщо подія вже оброблена - ігноруємо дублікати
                if (e.type === 'click' && eventHandled) {
                    console.log('Ignoring duplicate click after', e.type);
                    eventHandled = false;
                    return;
                }
                
                // Позначаємо що подію оброблено
                if (e.type === 'mousedown' || e.type === 'touchend') {
                    eventHandled = true;
                    setTimeout(() => { eventHandled = false; }, 300);
                }
                
                e.preventDefault();
                e.stopPropagation();
                
                console.log('Menu item', index, 'clicked via', e.type);
                
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
            }
            
            // Використовуємо Pointer Events API якщо доступно (сучасний підхід)
            if (window.PointerEvent) {
                console.log('Using Pointer Events for item', index);
                link.addEventListener('pointerdown', handleToggle, false);
                if (arrow) {
                    arrow.addEventListener('pointerdown', handleToggle, false);
                    arrow.style.cursor = 'pointer';
                }
            } else {
                // Fallback для старих браузерів
                console.log('Using Click/Touch Events for item', index);
                
                // Click - основна подія для desktop
                link.addEventListener('click', handleToggle, false);
                // Touchend - для мобільних пристроїв
                link.addEventListener('touchend', handleToggle, false);
                // Mousedown - запасний варіант для desktop
                link.addEventListener('mousedown', function(e) {
                    if (e.button === 0) { // Тільки ліва кнопка миші
                        handleToggle(e);
                    }
                }, false);
                
                // Додаємо обробник на стрілку
                if (arrow) {
                    arrow.addEventListener('click', handleToggle, false);
                    arrow.addEventListener('touchend', handleToggle, false);
                    arrow.addEventListener('mousedown', function(e) {
                        if (e.button === 0) {
                            handleToggle(e);
                        }
                    }, false);
                    arrow.style.cursor = 'pointer';
                }
            }
            
            // Для iOS Safari додаємо cursor: pointer через JavaScript
            link.style.cursor = 'pointer';
            
            // Дозволяємо клік по підкатегоріях (перехід на сторінку)
            const subLinks = submenu.querySelectorAll('.submenu__link');
            subLinks.forEach(subLink => {
                subLink.addEventListener('click', function(e) {
                    e.stopPropagation();
                    console.log('Submenu link clicked');
                    // Дозволяємо перехід на сторінку підкатегорії
                });
            });
        });
        
        // Додатковий метод через делегування подій (запасний варіант)
        const sidebar = document.querySelector('.sidebar-menu');
        if (sidebar) {
            sidebar.addEventListener('click', function(e) {
                const menuItem = e.target.closest('.sidebar-menu__item.has-children');
                const submenuLink = e.target.closest('.submenu__link');
                
                // Якщо клік по підменю - дозволяємо перехід
                if (submenuLink) {
                    console.log('Submenu link via delegation');
                    return;
                }
                
                // Якщо клік по головному меню з підменю
                if (menuItem && !submenuLink) {
                    const link = e.target.closest('.sidebar-menu__link');
                    if (link && link.parentElement === menuItem) {
                        console.log('Menu item via delegation');
                    }
                }
            });
        }
        
        // Відкриваємо активну категорію при завантаженні сторінки
        setTimeout(function() {
            const activeItem = document.querySelector('.sidebar-menu__item.active.has-children');
            if (activeItem && !activeItem.classList.contains('info-menu')) {
                console.log('Opening active menu item');
                openSubmenu(activeItem);
            }
        }, 100);
        
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
    }
    
    // Ініціалізація при завантаженні DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebarMenu);
    } else {
        // DOM вже завантажений
        initSidebarMenu();
    }
    
})();
