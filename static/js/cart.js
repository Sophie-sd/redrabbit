/**
 * Beauty Shop - Кошик
 * Функціонал роботи з кошиком
 */

class ShoppingCart {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.updateCartDisplay();
    }
    
    bindEvents() {
        // Додавання товару в кошик
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-cart') || e.target.closest('.add-to-cart')) {
                e.preventDefault();
                this.handleAddToCart(e.target.closest('.add-to-cart'));
            }
        });
        
        // Видалення товару з кошика
        document.addEventListener('click', (e) => {
            if (e.target.matches('.remove-from-cart') || e.target.closest('.remove-from-cart')) {
                e.preventDefault();
                this.handleRemoveFromCart(e.target.closest('.remove-from-cart'));
            }
        });
        
        // Зміна кількості товару
        document.addEventListener('change', (e) => {
            if (e.target.matches('.cart-quantity')) {
                this.handleQuantityChange(e.target);
            }
        });
        
        // Очищення кошика
        document.addEventListener('click', (e) => {
            if (e.target.matches('.clear-cart') || e.target.closest('.clear-cart')) {
                e.preventDefault();
                this.handleClearCart();
            }
        });
    }
    
    async handleAddToCart(button) {
        const productId = button.dataset.productId;
        const productName = button.dataset.productName;
        const quantity = this.getQuantityFromForm(button) || 1;
        
        if (!productId) {
            console.error('Product ID не знайдено');
            return;
        }
        
        // Показуємо індикатор завантаження
        this.setButtonLoading(button, true);
        
        try {
            const formData = new FormData();
            formData.append('quantity', quantity);
            
            const response = await BeautyShop.Ajax.postForm(`/cart/add/${productId}/`, formData);
            
            if (response) {
                this.showSuccessMessage(`${productName} додано в кошик`);
                this.updateCartDisplay();
                this.animateCartIcon();
            }
        } catch (error) {
            console.error('Помилка додавання в кошик:', error);
            this.showErrorMessage('Помилка додавання товару в кошик');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async handleRemoveFromCart(button) {
        const productId = button.dataset.productId;
        const productName = button.dataset.productName;
        
        if (!productId) {
            console.error('Product ID не знайдено');
            return;
        }
        
        // Підтвердження видалення
        if (!confirm(`Видалити ${productName} з кошика?`)) {
            return;
        }
        
        this.setButtonLoading(button, true);
        
        try {
            const formData = new FormData();
            const response = await BeautyShop.Ajax.postForm(`/cart/remove/${productId}/`, formData);
            
            if (response) {
                this.showSuccessMessage(`${productName} видалено з кошика`);
                this.updateCartDisplay();
                
                // Видаляємо рядок з таблиці кошика
                const cartRow = button.closest('.cart-item');
                if (cartRow) {
                    BeautyShop.Animations.fadeOut(cartRow, 300);
                    setTimeout(() => cartRow.remove(), 300);
                }
            }
        } catch (error) {
            console.error('Помилка видалення з кошика:', error);
            this.showErrorMessage('Помилка видалення товару з кошика');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async handleQuantityChange(input) {
        const productId = input.dataset.productId;
        const quantity = parseInt(input.value);
        
        if (!productId || quantity < 1) {
            return;
        }
        
        try {
            const formData = new FormData();
            formData.append('quantity', quantity);
            formData.append('override', 'true');
            
            await BeautyShop.Ajax.postForm(`/cart/add/${productId}/`, formData);
            this.updateCartDisplay();
            this.updateItemTotal(input);
        } catch (error) {
            console.error('Помилка оновлення кількості:', error);
            this.showErrorMessage('Помилка оновлення кількості');
        }
    }
    
    async handleClearCart() {
        if (!confirm('Очистити кошик?')) {
            return;
        }
        
        try {
            // Тут буде логіка очищення кошика
            this.showSuccessMessage('Кошик очищено');
            this.updateCartDisplay();
        } catch (error) {
            console.error('Помилка очищення кошика:', error);
            this.showErrorMessage('Помилка очищення кошика');
        }
    }
    
    getQuantityFromForm(button) {
        const form = button.closest('form');
        if (form) {
            const quantityInput = form.querySelector('input[name="quantity"]');
            return quantityInput ? parseInt(quantityInput.value) : 1;
        }
        return 1;
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = 'Додаємо...';
            button.classList.add('loading');
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || 'Купити';
            button.classList.remove('loading');
        }
    }
    
    async updateCartDisplay() {
        try {
            // Оновлюємо лічильник товарів в кошику
            const cartBadges = document.querySelectorAll('.cart-badge, .badge');
            const cartTotals = document.querySelectorAll('.cart-total');
            
            // Тут буде AJAX запит для отримання актуальної інформації про кошик
            // Поки що використовуємо заглушку
            const cartData = {
                itemCount: 0,
                totalPrice: 0
            };
            
            cartBadges.forEach(badge => {
                if (cartData.itemCount > 0) {
                    badge.textContent = cartData.itemCount;
                    badge.style.display = 'block';
                } else {
                    badge.style.display = 'none';
                }
            });
            
            cartTotals.forEach(total => {
                total.textContent = `${cartData.totalPrice.toFixed(2)} ₴`;
            });
        } catch (error) {
            console.error('Помилка оновлення відображення кошика:', error);
        }
    }
    
    updateItemTotal(quantityInput) {
        const cartItem = quantityInput.closest('.cart-item');
        if (!cartItem) return;
        
        const price = parseFloat(cartItem.dataset.price);
        const quantity = parseInt(quantityInput.value);
        const total = price * quantity;
        
        const totalElement = cartItem.querySelector('.item-total');
        if (totalElement) {
            totalElement.textContent = `${total.toFixed(2)} ₴`;
        }
        
        this.updateCartTotal();
    }
    
    updateCartTotal() {
        const cartItems = document.querySelectorAll('.cart-item');
        let total = 0;
        
        cartItems.forEach(item => {
            const itemTotal = item.querySelector('.item-total');
            if (itemTotal) {
                const itemPrice = parseFloat(itemTotal.textContent.replace(' ₴', ''));
                total += itemPrice;
            }
        });
        
        const totalElements = document.querySelectorAll('.cart-grand-total');
        totalElements.forEach(element => {
            element.textContent = `${total.toFixed(2)} ₴`;
        });
    }
    
    animateCartIcon() {
        const cartIcon = document.querySelector('.cart-link');
        if (cartIcon) {
            cartIcon.classList.add('cart-animation');
            setTimeout(() => {
                cartIcon.classList.remove('cart-animation');
            }, 600);
        }
    }
    
    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }
    
    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }
    
    showMessage(message, type = 'info') {
        // Створюємо повідомлення
        const messageDiv = BeautyShop.DOM.createElement('div', {
            className: `alert alert-${type} alert-dismissible fade show cart-message`,
            role: 'alert'
        }, [
            message,
            BeautyShop.DOM.createElement('button', {
                type: 'button',
                className: 'btn-close',
                'data-bs-dismiss': 'alert',
                'aria-label': 'Закрити'
            })
        ]);
        
        // Додаємо повідомлення на сторінку
        const container = document.querySelector('.messages-container') || document.body;
        container.appendChild(messageDiv);
        
        // Автоматично видаляємо через 5 секунд
        setTimeout(() => {
            if (messageDiv.parentNode) {
                BeautyShop.Animations.fadeOut(messageDiv, 300);
                setTimeout(() => messageDiv.remove(), 300);
            }
        }, 5000);
    }
}

// Ініціалізація кошика
BeautyShop.DOM.ready(() => {
    window.cart = new ShoppingCart();
});

// Додаємо стилі для анімації кошика
const style = document.createElement('style');
style.textContent = `
.cart-animation {
    animation: cartBounce 0.6s ease-in-out;
}

@keyframes cartBounce {
    0%, 100% { transform: scale(1); }
    25% { transform: scale(1.1); }
    50% { transform: scale(1.2); }
    75% { transform: scale(1.1); }
}

.btn.loading {
    opacity: 0.6;
    cursor: not-allowed;
}

.cart-message {
    position: fixed;
    top: 100px;
    right: 20px;
    z-index: 1050;
    min-width: 300px;
}

.alert-success {
    background-color: var(--success);
    border-color: var(--success);
    color: white;
}

.alert-error {
    background-color: var(--danger);
    border-color: var(--danger);
    color: white;
}
`;
document.head.appendChild(style);
