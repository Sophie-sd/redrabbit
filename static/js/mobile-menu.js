class MobileMenu {
    constructor() {
        this.catalogBtn = document.getElementById('catalogMenuBtn');
        this.catalogToggle = document.getElementById('catalogMenuToggle');
        this.menu = document.getElementById('mobile-menu');
        this.overlay = document.getElementById('mobile-menu-overlay');
        this.closeBtn = document.getElementById('mobile-menu-close');
        this.catalogSubmenu = document.querySelector('.mobile-submenu');
        this.body = document.body;
        this.isOpen = false;
        this.init();
    }

    init() {
        if (!this.menu || !this.overlay || !this.catalogBtn) {
            return;
        }
        this.bindEvents();
    }

    bindEvents() {
        if (this.catalogBtn) {
            this.catalogBtn.addEventListener('click', e => {
                e.preventDefault();
                e.stopPropagation();
                this.openMenu();
                setTimeout(() => {
                    if (this.catalogSubmenu && this.catalogToggle) {
                        this.catalogSubmenu.classList.add('active');
                        this.catalogToggle.classList.add('active');
                    }
                }, 100);
            });
        }

        if (this.catalogToggle) {
            this.catalogToggle.addEventListener('click', e => {
                e.preventDefault();
                e.stopPropagation();
                if (this.catalogSubmenu) {
                    this.catalogSubmenu.classList.toggle('active');
                    this.catalogToggle.classList.toggle('active');
                }
            });
        }

        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', e => {
                e.preventDefault();
                this.closeMenu();
            });
        }

        if (this.overlay) {
            this.overlay.addEventListener('click', () => {
                this.closeMenu();
            });
        }

        document.addEventListener('keydown', e => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeMenu();
            }
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth >= 992 && this.isOpen) {
                this.closeMenu();
            }
        });
    }

    toggleMenu() {
        this.isOpen ? this.closeMenu() : this.openMenu();
    }

    openMenu() {
        this.isOpen = true;
        this.menu.classList.add('active');
        this.overlay.classList.add('active');
        this.body.style.overflow = 'hidden';
        this.body.style.position = 'fixed';
        this.body.style.width = '100%';
        this.body.style.top = `-${window.scrollY}px`;
    }

    closeMenu() {
        const scrollY = Math.abs(parseInt(this.body.style.top || '0'));
        this.isOpen = false;
        this.menu.classList.remove('active');
        this.overlay.classList.remove('active');
        this.body.style.overflow = '';
        this.body.style.position = '';
        this.body.style.width = '';
        this.body.style.top = '';
        window.scrollTo(0, scrollY);
        
        if (this.catalogSubmenu) {
            this.catalogSubmenu.classList.remove('active');
        }
        if (this.catalogToggle) {
            this.catalogToggle.classList.remove('active');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new MobileMenu();
});

