// Scroll to Top Button - Тільки для Desktop
(function() {
    'use strict';
    
    // Перевірка чи Desktop
    function isDesktop() {
        return window.innerWidth >= 992;
    }
    
    // Створюємо кнопку
    const button = document.createElement('button');
    button.className = 'scroll-to-top';
    button.setAttribute('aria-label', 'Прокрутити вверх');
    button.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 19V5M12 5L5 12M12 5L19 12" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    `;
    
    // Додаємо кнопку до body
    document.body.appendChild(button);
    
    // Показуємо/ховаємо кнопку при скролі
    function toggleButton() {
        if (!isDesktop()) {
            button.classList.remove('visible');
            return;
        }
        
        if (window.pageYOffset > 300) {
            button.classList.add('visible');
        } else {
            button.classList.remove('visible');
        }
    }
    
    // Scroll to top
    function scrollToTop(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
    
    // Event listeners
    window.addEventListener('scroll', toggleButton, { passive: true });
    window.addEventListener('resize', toggleButton, { passive: true });
    button.addEventListener('click', scrollToTop);
    
    // Initial check
    toggleButton();
})();

