/**
 * Sale Page Banners Slider
 * Автоматична зміна банерів кожні 5 секунд + ручне керування
 */

class SaleBannerSlider {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        this.slides = this.container.querySelectorAll('.banner-slide');
        this.dotsContainer = this.container.querySelector('.banner-dots');
        this.prevBtn = this.container.querySelector('.banner-nav-prev');
        this.nextBtn = this.container.querySelector('.banner-nav-next');
        
        this.currentSlide = 0;
        this.autoplayInterval = null;
        this.autoplayDelay = 5000;
        
        this.init();
    }
    
    init() {
        if (this.slides.length <= 1) {
            if (this.prevBtn) this.prevBtn.style.display = 'none';
            if (this.nextBtn) this.nextBtn.style.display = 'none';
            if (this.dotsContainer) this.dotsContainer.style.display = 'none';
            return;
        }
        
        this.createDots();
        this.addEventListeners();
        this.startAutoplay();
    }
    
    createDots() {
        if (!this.dotsContainer) return;
        
        this.dotsContainer.innerHTML = '';
        
        this.slides.forEach((slide, index) => {
            const dot = document.createElement('button');
            dot.className = 'banner-dot';
            dot.setAttribute('aria-label', `Перейти до банера ${index + 1}`);
            
            if (index === 0) {
                dot.classList.add('active');
            }
            
            dot.addEventListener('click', () => {
                this.goToSlide(index);
                this.resetAutoplay();
            });
            
            this.dotsContainer.appendChild(dot);
        });
    }
    
    addEventListeners() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => {
                this.prevSlide();
                this.resetAutoplay();
            });
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => {
                this.nextSlide();
                this.resetAutoplay();
            });
        }
        
        this.container.addEventListener('mouseenter', () => {
            this.stopAutoplay();
        });
        
        this.container.addEventListener('mouseleave', () => {
            this.startAutoplay();
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                this.prevSlide();
                this.resetAutoplay();
            } else if (e.key === 'ArrowRight') {
                this.nextSlide();
                this.resetAutoplay();
            }
        });
        
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoplay();
            } else {
                this.startAutoplay();
            }
        });
    }
    
    goToSlide(index) {
        this.slides[this.currentSlide].classList.remove('active');
        
        const dots = this.dotsContainer?.querySelectorAll('.banner-dot');
        if (dots && dots[this.currentSlide]) {
            dots[this.currentSlide].classList.remove('active');
        }
        
        this.currentSlide = index;
        
        this.slides[this.currentSlide].classList.add('active');
        
        if (dots && dots[this.currentSlide]) {
            dots[this.currentSlide].classList.add('active');
        }
    }
    
    nextSlide() {
        const nextIndex = (this.currentSlide + 1) % this.slides.length;
        this.goToSlide(nextIndex);
    }
    
    prevSlide() {
        const prevIndex = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
        this.goToSlide(prevIndex);
    }
    
    startAutoplay() {
        if (this.slides.length <= 1) return;
        
        this.stopAutoplay();
        
        this.autoplayInterval = setInterval(() => {
            this.nextSlide();
        }, this.autoplayDelay);
    }
    
    stopAutoplay() {
        if (this.autoplayInterval) {
            clearInterval(this.autoplayInterval);
            this.autoplayInterval = null;
        }
    }
    
    resetAutoplay() {
        this.stopAutoplay();
        this.startAutoplay();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SaleBannerSlider('saleBannerSlider');
});

