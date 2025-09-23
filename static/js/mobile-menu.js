/**
 * Beauty Shop - Мобільне меню
 * Підтримка touch gestures та accessibility
 */

class MobileMenu {
    constructor() {
        this.menuBtn = document.getElementById('mobile-menu-btn');
        this.menu = document.getElementById('mobile-menu');
        this.overlay = document.getElementById('mobile-menu-overlay');
        this.closeBtn = document.getElementById('mobile-menu-close');
        this.body = document.body;
        this.isOpen = false;
        this.touchStartX = 0;
        this.touchEndX = 0;
        
        this.init();
    }
    
    init() {
        if (!this.menuBtn || !this.menu || !this.overlay) return;
        
        this.bindEvents();
        this.setupAccessibility();
        this.setupTouchGestures();
    }
    
    bindEvents() {
        // Відкриття меню
        this.menuBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMenu();
        });
        
        // Закриття меню
        this.closeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.closeMenu();
        });
        
        // Закриття по кліку на overlay
        this.overlay.addEventListener('click', () => {
            this.closeMenu();
        });
        
        // Закриття по ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeMenu();
            }
        });
        
        // Закриття при зміні розміру вікна
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 992 && this.isOpen) {
                this.closeMenu();
            }
        });
        
        // Закриття при кліку на посилання в меню
        const menuLinks = this.menu.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.closeMenu();
            });
        });
    }
    
    setupAccessibility() {
        // ARIA attributes
        this.menuBtn.setAttribute('aria-controls', 'mobile-menu');
        this.menu.setAttribute('aria-hidden', 'true');
        this.menu.setAttribute('tabindex', '-1');
        
        // Focus trap
        this.focusableElements = this.menu.querySelectorAll(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
    }
    
    setupTouchGestures() {
        // Swipe to close gesture
        this.menu.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        this.menu.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }, { passive: true });
        
        // Prevent scroll when menu is open
        this.menu.addEventListener('touchmove', (e) => {
            e.stopPropagation();
        }, { passive: true });
    }
    
    handleSwipe() {
        const swipeDistance = this.touchStartX - this.touchEndX;
        const minSwipeDistance = 100;
        
        // Swipe left to close
        if (swipeDistance > minSwipeDistance) {
            this.closeMenu();
        }
    }
    
    toggleMenu() {
        if (this.isOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }
    
    openMenu() {
        this.isOpen = true;
        this.menu.classList.add('active');
        this.overlay.classList.add('active');
        this.body.classList.add('menu-open');
        
        // ARIA updates
        this.menuBtn.setAttribute('aria-expanded', 'true');
        this.menu.setAttribute('aria-hidden', 'false');
        
        // Focus management
        this.menu.focus();
        this.trapFocus();
        
        // Animate hamburger
        this.menuBtn.classList.add('active');
        
        // Prevent body scroll
        this.preventBodyScroll();
        
        // Analytics
        this.trackEvent('mobile_menu_open');
    }
    
    closeMenu() {
        this.isOpen = false;
        this.menu.classList.remove('active');
        this.overlay.classList.remove('active');
        this.body.classList.remove('menu-open');
        
        // ARIA updates
        this.menuBtn.setAttribute('aria-expanded', 'false');
        this.menu.setAttribute('aria-hidden', 'true');
        
        // Return focus to menu button
        this.menuBtn.focus();
        
        // Animate hamburger
        this.menuBtn.classList.remove('active');
        
        // Allow body scroll
        this.allowBodyScroll();
        
        // Analytics
        this.trackEvent('mobile_menu_close');
    }
    
    trapFocus() {
        if (!this.focusableElements.length) return;
        
        const firstElement = this.focusableElements[0];
        const lastElement = this.focusableElements[this.focusableElements.length - 1];
        
        this.menu.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    // Shift + Tab
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    // Tab
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        });
    }
    
    preventBodyScroll() {
        const scrollY = window.scrollY;
        this.body.style.position = 'fixed';
        this.body.style.top = `-${scrollY}px`;
        this.body.style.width = '100%';
        this.body.dataset.scrollY = scrollY;
    }
    
    allowBodyScroll() {
        const scrollY = this.body.dataset.scrollY;
        this.body.style.position = '';
        this.body.style.top = '';
        this.body.style.width = '';
        window.scrollTo(0, parseInt(scrollY || '0'));
        delete this.body.dataset.scrollY;
    }
    
    trackEvent(action) {
        // Google Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                event_category: 'Mobile Menu',
                event_label: 'User Interaction'
            });
        }
    }
}

// Submenu functionality for mobile
class MobileSubmenu {
    constructor() {
        this.submenus = document.querySelectorAll('.mobile-submenu');
        this.init();
    }
    
    init() {
        this.submenus.forEach(submenu => {
            const title = submenu.querySelector('.submenu-title');
            const list = submenu.querySelector('.submenu-list');
            
            if (title && list) {
                title.addEventListener('click', () => {
                    const isActive = submenu.classList.contains('active');
                    
                    // Close all other submenus
                    this.submenus.forEach(s => s.classList.remove('active'));
                    
                    // Toggle current submenu
                    if (!isActive) {
                        submenu.classList.add('active');
                    }
                });
                
                // Add ARIA attributes
                title.setAttribute('role', 'button');
                title.setAttribute('aria-expanded', 'false');
                title.setAttribute('tabindex', '0');
                
                // Keyboard support
                title.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        title.click();
                    }
                });
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MobileMenu();
    new MobileSubmenu();
});

// Handle orientation change
window.addEventListener('orientationchange', () => {
    // Small delay to allow for orientation change to complete
    setTimeout(() => {
        // Update viewport height for mobile browsers
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }, 100);
});

// Set initial viewport height
const vh = window.innerHeight * 0.01;
document.documentElement.style.setProperty('--vh', `${vh}px`);
