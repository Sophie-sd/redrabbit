// Слайдер відгуків клієнтів
document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('reviewsSlider');
    const prevBtn = document.querySelector('.reviews-prev-btn');
    const nextBtn = document.querySelector('.reviews-next-btn');
    const indicators = document.querySelectorAll('.indicator');
    
    if (!slider || !prevBtn || !nextBtn) return;
    
    let currentSlide = 0;
    const totalReviews = document.querySelectorAll('.review-item').length;
    let reviewsPerSlide = window.innerWidth <= 768 ? 1 : 2; // 1 для мобільних, 2 для десктопу
    let totalSlides = Math.ceil(totalReviews / reviewsPerSlide);
    
    // Функція для оновлення кількості відгуків на слайді при зміні розміру екрану
    function updateReviewsPerSlide() {
        const newReviewsPerSlide = window.innerWidth <= 768 ? 1 : 2;
        if (newReviewsPerSlide !== reviewsPerSlide) {
            reviewsPerSlide = newReviewsPerSlide;
            totalSlides = Math.ceil(totalReviews / reviewsPerSlide);
            currentSlide = Math.min(currentSlide, totalSlides - 1);
            updateSlider();
        }
    }
    
    // Функція для оновлення позиції слайдера
    function updateSlider() {
        const translateX = -currentSlide * 100;
        slider.style.transform = `translateX(${translateX}%)`;
        
        // Оновлення індикаторів
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === currentSlide);
        });
        
        // Додаємо клас active до поточних слайдів
        document.querySelectorAll('.review-item').forEach((item, index) => {
            const isActive = index >= currentSlide * reviewsPerSlide && index < (currentSlide + 1) * reviewsPerSlide;
            item.classList.toggle('active', isActive);
        });
    }
    
    // Функція для переходу до наступного слайду
    function nextSlide() {
        currentSlide = (currentSlide + 1) % totalSlides;
        updateSlider();
    }
    
    // Функція для переходу до попереднього слайду
    function prevSlide() {
        currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
        updateSlider();
    }
    
    // Функція для переходу до конкретного слайду
    function goToSlide(slideIndex) {
        currentSlide = slideIndex;
        updateSlider();
    }
    
    // Обробники подій
    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);
    
    // Обробники для індикаторів
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => goToSlide(index));
    });
    
    // Автоматичне прокручування (опціонально)
    let autoSlideInterval;
    
    function startAutoSlide() {
        autoSlideInterval = setInterval(nextSlide, 5000); // 5 секунд
    }
    
    function stopAutoSlide() {
        clearInterval(autoSlideInterval);
    }
    
    // Запускаємо автоматичне прокручування
    startAutoSlide();
    
    // Зупиняємо автоматичне прокручування при hover
    const sliderContainer = document.querySelector('.reviews-slider-container');
    if (sliderContainer) {
        sliderContainer.addEventListener('mouseenter', stopAutoSlide);
        sliderContainer.addEventListener('mouseleave', startAutoSlide);
    }
    
    // Підтримка сенсорних пристроїв
    let startX = 0;
    let isDragging = false;
    
    slider.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        isDragging = true;
        stopAutoSlide();
    });
    
    slider.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        e.preventDefault();
    });
    
    slider.addEventListener('touchend', (e) => {
        if (!isDragging) return;
        
        const endX = e.changedTouches[0].clientX;
        const diffX = startX - endX;
        
        // Мінімальна відстань для свайпу
        if (Math.abs(diffX) > 50) {
            if (diffX > 0) {
                nextSlide();
            } else {
                prevSlide();
            }
        }
        
        isDragging = false;
        startAutoSlide();
    });
    
    // Підтримка клавіатури
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            prevSlide();
        } else if (e.key === 'ArrowRight') {
            nextSlide();
        }
    });
    
    // Обробник зміни розміру вікна
    window.addEventListener('resize', updateReviewsPerSlide);
    
    // Ініціалізація
    updateSlider();
});
