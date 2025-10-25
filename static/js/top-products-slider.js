document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('topProductsSlider');
    if (!slider) return;

    const container = slider.closest('.promotions-slider-container');
    const prevBtn = container.querySelector('.promo-prev-btn');
    const nextBtn = container.querySelector('.promo-next-btn');
    const cards = slider.querySelectorAll('.promo-card');
    
    if (cards.length === 0) return;
    
    function getScrollAmount() {
        const cardWidth = cards[0].offsetWidth;
        const gap = 20;
        return (cardWidth + gap) * 4;
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            slider.scrollBy({ left: getScrollAmount(), behavior: 'smooth' });
        });
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            slider.scrollBy({ left: -getScrollAmount(), behavior: 'smooth' });
        });
    }
});

