/**
 * Слайдер акційних пропозицій
 */

document.addEventListener('DOMContentLoaded', function() {
    // Ініціалізуємо обидва слайдери (мобільний і десктопний)
    initPromotionsSlider('promotionsSlider');
    initPromotionsSlider('promotionsSliderDesktop');
});

function initPromotionsSlider(sliderId) {
    const slider = document.getElementById(sliderId);
    if (!slider) return;
    
    const container = slider.closest('.promotions-slider-container');
    const prevBtn = container.querySelector('.promo-prev-btn');
    const nextBtn = container.querySelector('.promo-next-btn');
    const cards = slider.querySelectorAll('.promo-card');
    
    if (cards.length === 0) return;
    
    // Функція для розрахунку ширини прокрутки (4 картки)
    function getScrollAmount() {
        const cardWidth = cards[0].offsetWidth;
        const gap = 20;
        return (cardWidth + gap) * 4;
    }
    
    // Функція прокрутки
    function scrollSlider(direction) {
        const scrollAmount = getScrollAmount();
        
        slider.scrollBy({
            left: direction === 'next' ? scrollAmount : -scrollAmount,
            behavior: 'smooth'
        });
    }
    
    // Обробники кнопок навігації
    if (prevBtn) {
        prevBtn.addEventListener('click', () => scrollSlider('prev'));
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => scrollSlider('next'));
    }
    
    // Свайп на мобільних
    let startX = 0;
    let scrollLeft = 0;
    let isDown = false;
    
    slider.addEventListener('mousedown', (e) => {
        isDown = true;
        startX = e.pageX - slider.offsetLeft;
        scrollLeft = slider.scrollLeft;
        slider.style.cursor = 'grabbing';
    });
    
    slider.addEventListener('mouseleave', () => {
        isDown = false;
        slider.style.cursor = 'grab';
    });
    
    slider.addEventListener('mouseup', () => {
        isDown = false;
        slider.style.cursor = 'grab';
    });
    
    slider.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - slider.offsetLeft;
        const walk = (x - startX) * 2;
        slider.scrollLeft = scrollLeft - walk;
    });
    
    // Touch events для мобільних
    let touchStartX = 0;
    let touchScrollLeft = 0;
    
    slider.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].pageX;
        touchScrollLeft = slider.scrollLeft;
    });
    
    slider.addEventListener('touchmove', (e) => {
        const touchX = e.touches[0].pageX;
        const walk = (touchX - touchStartX) * 2;
        slider.scrollLeft = touchScrollLeft - walk;
    });
    
    // Клавіатурна навігація
    slider.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            scrollSlider('prev');
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            scrollSlider('next');
        }
    });
    
    // Оновлюємо видимість кнопок при прокрутці
    function updateButtons() {
        if (!prevBtn || !nextBtn) return;
        
        const isAtStart = slider.scrollLeft <= 0;
        const isAtEnd = slider.scrollLeft >= slider.scrollWidth - slider.clientWidth - 1;
        
        prevBtn.style.opacity = isAtStart ? '0.5' : '1';
        prevBtn.style.cursor = isAtStart ? 'not-allowed' : 'pointer';
        
        nextBtn.style.opacity = isAtEnd ? '0.5' : '1';
        nextBtn.style.cursor = isAtEnd ? 'not-allowed' : 'pointer';
    }
    
    slider.addEventListener('scroll', updateButtons);
    updateButtons();
    
    // Оновлюємо при зміні розміру вікна
    window.addEventListener('resize', () => {
        updateButtons();
    });
}

