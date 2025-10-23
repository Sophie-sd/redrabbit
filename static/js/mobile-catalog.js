document.addEventListener('DOMContentLoaded', function() {
    const catalogBtn = document.getElementById('catalogMenuBtn');
    const catalogToggle = document.getElementById('catalogMenuToggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    function toggleCatalog() {
        if (mobileMenu) {
            const categoriesSection = mobileMenu.querySelector('.mobile-submenu');
            if (categoriesSection) {
                categoriesSection.classList.toggle('expanded');
                const isExpanded = categoriesSection.classList.contains('expanded');
                categoriesSection.setAttribute('aria-expanded', isExpanded);
            } else {
                if (!mobileMenu.classList.contains('active')) {
                    mobileMenu.classList.add('active');
                }
            }
        }
    }
    
    if (catalogBtn) {
        catalogBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleCatalog();
        });
    }
    
    if (catalogToggle) {
        catalogToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleCatalog();
        });
    }
});

