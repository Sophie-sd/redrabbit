(function() {
    'use strict';
    
    function initMobileCatalog() {
        const catalogBtn = document.getElementById('catalogMenuBtn');
        const catalogToggle = document.getElementById('catalogMenuToggle');
        const menu = document.getElementById('mobile-menu');
        const overlay = document.getElementById('mobile-menu-overlay');
        const closeBtn = document.getElementById('mobile-menu-close');
        
        if (!catalogBtn || !catalogToggle) {
            console.warn('Mobile catalog buttons not found');
            return;
        }
        
        if (!menu || !overlay) {
            console.error('Mobile menu elements not found');
            return;
        }
        
        catalogBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const submenu = document.querySelector('.mobile-submenu');
            
            menu.classList.add('active');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            document.body.style.position = 'fixed';
            document.body.style.width = '100%';
            
            setTimeout(function() {
                if (submenu) {
                    submenu.classList.add('active');
                    catalogToggle.classList.add('active');
                }
            }, 350);
        });
        
        catalogToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const submenu = document.querySelector('.mobile-submenu');
            if (submenu) {
                submenu.classList.toggle('active');
                catalogToggle.classList.toggle('active');
            }
        });
        
        function resetCatalogState() {
            const submenu = document.querySelector('.mobile-submenu');
            if (submenu) {
                submenu.classList.remove('active');
            }
            catalogToggle.classList.remove('active');
        }
        
        if (closeBtn) {
            closeBtn.addEventListener('click', resetCatalogState);
        }
        
        if (overlay) {
            overlay.addEventListener('click', resetCatalogState);
        }
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileCatalog);
    } else {
        initMobileCatalog();
    }
})();

