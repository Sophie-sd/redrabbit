/**
 * Інтеграція оновлення badge кошика з основним функціоналом
 * Слухає події від cart.min.js та оновлює мобільний badge
 */

(function() {
    'use strict';

    /**
     * Оновлення всіх badge кошика (десктоп і мобільний)
     */
    function updateAllCartBadges(count) {
        // Оновлюємо мобільний badge через функцію з mobile-cart-badge.js
        if (typeof window.updateMobileCartBadge === 'function') {
            window.updateMobileCartBadge(count);
        }

        // Оновлюємо десктопні badge
        document.querySelectorAll('.cart-link .badge').forEach(badge => {
            if (count > 0) {
                badge.textContent = count;
                badge.classList.remove('badge-hidden');
            } else {
                badge.textContent = '';
                badge.classList.add('badge-hidden');
            }
        });

        // Зберігаємо в localStorage для синхронізації між вкладками
        try {
            localStorage.setItem('cart_count', count);
        } catch (e) {
            console.warn('Не вдалося зберегти кількість товарів у localStorage');
        }
    }

    /**
     * Отримання кількості товарів з API
     */
    async function refreshCartCount() {
        try {
            const response = await fetch('/cart/api/count/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                const count = data.count || 0;
                updateAllCartBadges(count);
                
                // Відправляємо custom event
                document.dispatchEvent(new CustomEvent('cart:updated', {
                    detail: { count }
                }));
            }
        } catch (error) {
            console.error('Помилка оновлення кількості товарів у кошику:', error);
        }
    }

    /**
     * Патчимо існуючий ShoppingCart клас
     */
    function patchShoppingCart() {
        // Якщо ShoppingCart вже завантажений
        if (window.cart && typeof window.cart.updateCartDisplay === 'function') {
            const originalUpdate = window.cart.updateCartDisplay;
            
            window.cart.updateCartDisplay = async function() {
                await originalUpdate.call(this);
                await refreshCartCount();
            };
        }
    }

    /**
     * Ініціалізація при завантаженні
     */
    function init() {
        // Оновлюємо badge при завантаженні
        refreshCartCount();

        // Патчимо ShoppingCart якщо він вже існує
        patchShoppingCart();

        // Слухаємо події додавання в кошик
        document.addEventListener('click', async function(event) {
            const addButton = event.target.closest('.add-to-cart');
            if (addButton) {
                // Даємо час на виконання оригінального обробника
                setTimeout(refreshCartCount, 500);
            }
        });

        // Слухаємо події видалення з кошика
        document.addEventListener('click', async function(event) {
            const removeButton = event.target.closest('.remove-from-cart');
            if (removeButton) {
                setTimeout(refreshCartCount, 500);
            }
        });

        // Слухаємо зміни кількості
        document.addEventListener('change', async function(event) {
            if (event.target.matches('.cart-quantity')) {
                setTimeout(refreshCartCount, 500);
            }
        });
    }

    // Запускаємо при завантаженні DOM або одразу якщо DOM вже завантажений
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Патчимо після завантаження всіх скриптів
    window.addEventListener('load', patchShoppingCart);
})();

