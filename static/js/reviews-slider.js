document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('reviewsSlider');
    if (!slider) return;

    const prevBtn = document.querySelector('.reviews-section .reviews-prev-btn');
    const nextBtn = document.querySelector('.reviews-section .reviews-next-btn');
    
    if (!prevBtn || !nextBtn) return;

    function getScrollAmount() {
        if (window.innerWidth <= 768) {
            const card = slider.querySelector('.review-card');
            if (card) {
                return card.offsetWidth + 20;
            }
            return window.innerWidth - 80;
        }
        return (380 + 24) * 2;
    }

    function updateButtons() {
        const scrollLeft = slider.scrollLeft;
        const maxScroll = slider.scrollWidth - slider.clientWidth;

        prevBtn.disabled = scrollLeft <= 0;
        nextBtn.disabled = scrollLeft >= maxScroll - 10;
    }

    prevBtn.addEventListener('click', () => {
        slider.scrollBy({
            left: -getScrollAmount(),
            behavior: 'smooth'
        });
    });

    nextBtn.addEventListener('click', () => {
        slider.scrollBy({
            left: getScrollAmount(),
            behavior: 'smooth'
        });
    });

    slider.addEventListener('scroll', updateButtons);
    
    updateButtons();

    window.addEventListener('resize', updateButtons);

    document.querySelectorAll('.review-read-more').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const textElement = this.previousElementSibling;
            const card = this.closest('.review-card');
            
            if (textElement.classList.contains('collapsed')) {
                textElement.classList.remove('collapsed');
                textElement.classList.add('expanded');
                card.classList.add('expanded');
                this.textContent = 'Згорнути ↑';
            } else {
                textElement.classList.remove('expanded');
                textElement.classList.add('collapsed');
                card.classList.remove('expanded');
                this.textContent = 'Читати далі →';
            }
        });
    });
});
