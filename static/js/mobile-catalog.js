document.addEventListener('DOMContentLoaded', function() {
    const catalogBtn = document.getElementById('catalogMenuBtn');
    const catalogToggle = document.getElementById('catalogMenuToggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-menu-overlay');
    const closeBtn = document.getElementById('mobile-menu-close');
    
    function openMobileMenuWithCatalog() {
        if (!mobileMenu || !overlay) return;
        
        mobileMenu.classList.add('active');
        overlay.classList.add('active');
        document.body.classList.add('menu-open');
        document.body.style.overflow = 'hidden';
        
        setTimeout(() => {
            const catalogToggleBtn = document.getElementById('catalogMenuToggle');
            if (catalogToggleBtn) {
                catalogToggleBtn.click();
            }
        }, 300);
    }
    
    function closeMobileMenu() {
        if (!mobileMenu || !overlay) return;
        
        mobileMenu.classList.remove('active');
        overlay.classList.remove('active');
        document.body.classList.remove('menu-open');
        document.body.style.overflow = '';
    }
    
    if (catalogBtn) {
        catalogBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            openMobileMenuWithCatalog();
        });
    }
    
    if (catalogToggle) {
        catalogToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const categoriesSection = document.querySelector('.mobile-submenu');
            if (categoriesSection) {
                categoriesSection.classList.toggle('active');
                const title = categoriesSection.querySelector('.submenu-title');
                if (title) {
                    const isActive = categoriesSection.classList.contains('active');
                    title.setAttribute('aria-expanded', isActive.toString());
                }
            }
        });
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeMobileMenu);
    }
    
    if (overlay) {
        overlay.addEventListener('click', closeMobileMenu);
    }
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    });
});

