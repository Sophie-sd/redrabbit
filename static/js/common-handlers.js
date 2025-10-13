/**
 * Common Event Handlers
 * Загальні обробники подій для сайту Beauty Shop
 */

(function() {
    'use strict';

    // Accordion toggles (для мобільного футера)
    function initAccordions() {
        const accordionToggles = document.querySelectorAll('[data-accordion-toggle]');
        
        accordionToggles.forEach(button => {
            button.addEventListener('click', function() {
                const item = this.parentElement;
                const content = item.querySelector('.accordion-content');
                
                // Закриваємо всі інші акордеони
                document.querySelectorAll('.accordion-item').forEach(otherItem => {
                    if (otherItem !== item && otherItem.classList.contains('active')) {
                        otherItem.classList.remove('active');
                        const otherContent = otherItem.querySelector('.accordion-content');
                        if (otherContent) {
                            otherContent.style.maxHeight = null;
                        }
                    }
                });
                
                // Перемикаємо поточний акордеон
                item.classList.toggle('active');
                
                if (item.classList.contains('active')) {
                    content.style.maxHeight = content.scrollHeight + 'px';
                } else {
                    content.style.maxHeight = null;
                }
            });
        });
    }

    // Cancel order handler
    function initCancelOrderButtons() {
        const cancelButtons = document.querySelectorAll('[data-cancel-order]');
        
        cancelButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const orderId = this.getAttribute('data-cancel-order');
                
                if (confirm('Ви впевнені, що хочете скасувати це замовлення?')) {
                    // AJAX запит на скасування
                    if (window.BeautyShop && window.BeautyShop.Ajax) {
                        window.BeautyShop.Ajax.post('/orders/cancel/', { order_id: orderId })
                            .then(response => {
                                if (response.success) {
                                    location.reload();
                                } else {
                                    alert(response.error || 'Помилка скасування замовлення');
                                }
                            })
                            .catch(error => {
                                console.error('Cancel order error:', error);
                                alert('Помилка скасування замовлення');
                            });
                    }
                }
            });
        });
    }

    // Confirm links (для підтвердження дій)
    function initConfirmLinks() {
        const confirmLinks = document.querySelectorAll('[data-confirm]');
        
        confirmLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const message = this.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    }

    // Alert close buttons
    function initAlertCloseButtons() {
        const closeButtons = document.querySelectorAll('.alert-close');
        
        closeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const alert = this.closest('.alert');
                if (alert && window.BeautyShop && window.BeautyShop.Animations) {
                    window.BeautyShop.Animations.fadeOut(alert, 200);
                } else if (alert) {
                    alert.style.display = 'none';
                }
            });
        });
    }

    // Ініціалізація при завантаженні DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initAccordions();
            initCancelOrderButtons();
            initConfirmLinks();
            initAlertCloseButtons();
        });
    } else {
        initAccordions();
        initCancelOrderButtons();
        initConfirmLinks();
        initAlertCloseButtons();
    }
})();

