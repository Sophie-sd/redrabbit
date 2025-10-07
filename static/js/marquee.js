/**
 * Marquee Animation Controller
 * Контролює біжучу стрічку з промо-повідомленнями
 */
class MarqueeController {
    constructor() {
        this.marquees = document.querySelectorAll('.marquee-container');
        this.init();
    }

    init() {
        this.marquees.forEach(marquee => {
            this.setupMarquee(marquee);
        });
    }

    setupMarquee(marquee) {
        const content = marquee.querySelector('.marquee-content');
        
        if (!content) return;

        // Пауза при наведенні миші
        marquee.addEventListener('mouseenter', () => {
            content.style.animationPlayState = 'paused';
        });

        // Відновлення анімації після виходу миші
        marquee.addEventListener('mouseleave', () => {
            content.style.animationPlayState = 'running';
        });

        // Пауза при фокусі (для доступності)
        marquee.addEventListener('focusin', () => {
            content.style.animationPlayState = 'paused';
        });

        marquee.addEventListener('focusout', () => {
            content.style.animationPlayState = 'running';
        });

        // Адаптивна швидкість анімації залежно від розміру екрану
        this.adjustAnimationSpeed(marquee, content);
        
        // Відслідковування зміни розміру екрану
        window.addEventListener('resize', () => {
            this.adjustAnimationSpeed(marquee, content);
        });

        // Інтеграція з prefers-reduced-motion
        this.handleReducedMotion(content);
    }

    adjustAnimationSpeed(marquee, content) {
        const screenWidth = window.innerWidth;
        let duration;

        if (screenWidth >= 1200) {
            duration = '45s';
        } else if (screenWidth >= 992) {
            duration = '38s'; // Швидше для планшетів
        } else if (screenWidth >= 768) {
            duration = '38s'; // Швидше для планшетів
        } else if (screenWidth >= 576) {
            duration = '18s'; // Швидше в 2 рази для мобільних
        } else {
            duration = '20s'; // Швидше в 2 рази для маленьких екранів
        }

        content.style.animationDuration = duration;
    }

    handleReducedMotion(content) {
        // Перевірка системної настройки reduce-motion
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        
        const setReducedMotion = (mediaQuery) => {
            if (mediaQuery.matches) {
                content.style.animationDuration = '120s';
            }
        };

        // Встановлення початкового стану
        setReducedMotion(prefersReducedMotion);
        
        // Відслідковування змін настройки
        prefersReducedMotion.addEventListener('change', setReducedMotion);
    }

    // Метод для програмного контролю анімації
    pauseAll() {
        this.marquees.forEach(marquee => {
            const content = marquee.querySelector('.marquee-content');
            if (content) {
                content.style.animationPlayState = 'paused';
            }
        });
    }

    resumeAll() {
        this.marquees.forEach(marquee => {
            const content = marquee.querySelector('.marquee-content');
            if (content) {
                content.style.animationPlayState = 'running';
            }
        });
    }

    // Метод для оновлення тексту біжучої стрічки
    updateText(newText) {
        this.marquees.forEach(marquee => {
            const textElement = marquee.querySelector('.marquee-text');
            if (textElement) {
                textElement.innerHTML = newText;
            }
        });
    }
}

// Ініціалізація після завантаження DOM
document.addEventListener('DOMContentLoaded', () => {
    // Перевірка чи є біжучі стрічки на сторінці
    if (document.querySelector('.marquee-container')) {
        window.marqueeController = new MarqueeController();
    }
});

// Performance optimization: використовуємо passive listeners для touch events
document.addEventListener('touchstart', () => {}, { passive: true });
document.addEventListener('touchmove', () => {}, { passive: true });

// Експорт для використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MarqueeController;
}
