document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('reviewsSlider');
    if (!slider) return;

    const prevBtn = document.querySelector('.reviews-section .reviews-prev-btn');
    const nextBtn = document.querySelector('.reviews-section .reviews-next-btn');
    
    if (!prevBtn || !nextBtn) return;

    const cardWidth = 350 + 24;
    const scrollAmount = cardWidth * 2;

    function updateButtons() {
        const scrollLeft = slider.scrollLeft;
        const maxScroll = slider.scrollWidth - slider.clientWidth;

        prevBtn.disabled = scrollLeft <= 0;
        nextBtn.disabled = scrollLeft >= maxScroll - 10;
    }

    prevBtn.addEventListener('click', () => {
        slider.scrollBy({
            left: -scrollAmount,
            behavior: 'smooth'
        });
    });

    nextBtn.addEventListener('click', () => {
        slider.scrollBy({
            left: scrollAmount,
            behavior: 'smooth'
        });
    });

    slider.addEventListener('scroll', updateButtons);
    
    updateButtons();

    window.addEventListener('resize', updateButtons);
});
