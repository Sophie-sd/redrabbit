setTimeout(function() {
    const catalogBtn = document.getElementById('catalogMenuBtn');
    const catalogToggle = document.getElementById('catalogMenuToggle');
    
    if (catalogBtn) {
        catalogBtn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const menu = document.getElementById('mobile-menu');
            const overlay = document.getElementById('mobile-menu-overlay');
            
            if (menu && overlay) {
                menu.classList.add('active');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
                
                setTimeout(function() {
                    const submenu = menu.querySelector('.mobile-submenu');
                    if (submenu) submenu.classList.add('active');
                }, 400);
            }
            return false;
        };
    }
    
    if (catalogToggle) {
        catalogToggle.onclick = function(e) {
            e.preventDefault();
            const submenu = document.querySelector('.mobile-submenu');
            if (submenu) submenu.classList.toggle('active');
            return false;
        };
    }
}, 500);

