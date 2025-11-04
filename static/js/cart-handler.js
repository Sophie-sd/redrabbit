/**
 * Cart Handler - Універсальний обробник додавання в кошик
 */

(function() {
    'use strict';

    class CartHandler {
        constructor() {
            this.init();
        }

        init() {
            this.bindCartButtons();
            
            document.addEventListener('DOMContentLoaded', () => {
                this.bindCartButtons();
            });
        }

        bindCartButtons() {
            const buttons = document.querySelectorAll('.product-card__add-cart, .btn-add-cart, .add-to-cart');
            
            buttons.forEach(button => {
                if (button.hasAttribute('data-cart-initialized')) return;
                button.setAttribute('data-cart-initialized', 'true');
                
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.addToCart(button);
                });
            });
        }

        async addToCart(button) {
            const productId = button.dataset.productId;
            
            if (!productId) {
                console.error('Product ID not found');
                return;
            }

            if (button.disabled) return;
            
            button.disabled = true;
            const originalHTML = button.innerHTML;
            button.innerHTML = 'Додається...';

            try {
                const response = await fetch(`/cart/add/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ quantity: 1 })
                });

                const data = await response.json();

                if (data.success) {
                    if (window.Toast) {
                        window.Toast.success('Товар додано в кошик');
                    }
                    
                    document.dispatchEvent(new CustomEvent('cart:updated', {
                        detail: { count: data.cart_count }
                    }));

                    button.innerHTML = '✓ Додано';
                    setTimeout(() => {
                        button.innerHTML = originalHTML;
                        button.disabled = false;
                    }, 2000);
                } else {
                    throw new Error(data.message || 'Помилка додавання');
                }
            } catch (error) {
                console.error('Cart add error:', error);
                if (window.Toast) {
                    window.Toast.error('Помилка при додаванні в кошик');
                }
                button.innerHTML = originalHTML;
                button.disabled = false;
            }
        }

        getCSRFToken() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            if (token) return token;
            
            const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
            return cookie ? cookie.split('=')[1] : '';
        }
    }

    const cartHandler = new CartHandler();
    
    window.CartHandler = CartHandler;
    window.cartHandler = cartHandler;
})();

