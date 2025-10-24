document.addEventListener('DOMContentLoaded', function() {
    console.log('Mobile Catalog: Initializing...');
    
    const catalogBtn = document.getElementById('catalogMenuBtn');
    const catalogToggle = document.getElementById('catalogMenuToggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-menu-overlay');
    
    console.log('Mobile Catalog: Elements found:', {
        catalogBtn: !!catalogBtn,
        catalogToggle: !!catalogToggle,
        mobileMenu: !!mobileMenu,
        overlay: !!overlay
    });
    
    function openMobileMenuWithCatalog() {
        console.log('Mobile Catalog: Opening menu with catalog');
        
        if (!mobileMenu || !overlay) {
            console.error('Mobile Catalog: Menu or overlay not found');
            return;
        }
        
        mobileMenu.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        setTimeout(() => {
            const submenu = mobileMenu.querySelector('.mobile-submenu');
            if (submenu) {
                console.log('Mobile Catalog: Showing submenu');
                submenu.classList.add('active');
            } else {
                console.error('Mobile Catalog: Submenu not found');
            }
        }, 350);
    }
    
    if (catalogBtn) {
        console.log('Mobile Catalog: Adding click listener to catalog button');
        catalogBtn.addEventListener('click', function(e) {
            console.log('Mobile Catalog: Catalog button clicked');
            e.preventDefault();
            e.stopPropagation();
            openMobileMenuWithCatalog();
        });
        
        catalogBtn.addEventListener('touchend', function(e) {
            console.log('Mobile Catalog: Catalog button touched');
            e.preventDefault();
            e.stopPropagation();
            openMobileMenuWithCatalog();
        }, { passive: false });
    } else {
        console.error('Mobile Catalog: Catalog button not found!');
    }
    
    if (catalogToggle) {
        console.log('Mobile Catalog: Adding click listener to catalog toggle');
        catalogToggle.addEventListener('click', function(e) {
            console.log('Mobile Catalog: Catalog toggle clicked');
            e.preventDefault();
            e.stopPropagation();
            const submenu = mobileMenu.querySelector('.mobile-submenu');
            if (submenu) {
                submenu.classList.toggle('active');
                console.log('Mobile Catalog: Toggled submenu, active:', submenu.classList.contains('active'));
            }
        });
    }
});

