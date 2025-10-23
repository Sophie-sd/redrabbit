document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('topProductsSlider');
    if (!slider) return;

    const container = slider.closest('.promotions-slider-container');
    const prevBtn = container.querySelector('.promo-prev-btn');
    const nextBtn = container.querySelector('.promo-next-btn');
    
    const scrollAmount = 300;
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            slider.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        });
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            slider.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        });
    }
});

