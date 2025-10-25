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
        const isMobile = window.innerWidth <= 768;
        const gap = isMobile ? 10 : 15;
        const cardsToScroll = isMobile ? 2 : 4;
        return (cardWidth + gap) * cardsToScroll;
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

