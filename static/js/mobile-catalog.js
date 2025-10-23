document.addEventListener('DOMContentLoaded', function() {
    const catalogBtn = document.getElementById('catalogMenuBtn');
    const catalogToggle = document.getElementById('catalogMenuToggle');
    const mobileMenuToggle = document.querySelector('[data-mobile-menu-toggle]');

    function openMobileMenu() {
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu && mobileMenuToggle) {
            mobileMenu.classList.add('active');
            mobileMenuToggle.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden';

            setTimeout(() => {
                const categoriesSection = document.querySelector('.mobile-submenu');
                if (categoriesSection) {
                    categoriesSection.classList.add('active');
                    const title = categoriesSection.querySelector('.submenu-title');
                    if (title) {
                        title.setAttribute('aria-expanded', 'true');
                    }
                }
            }, 100);
        }
    }

    if (catalogBtn) {
        catalogBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            openMobileMenu();
        });
    }

    if (catalogToggle) {
        catalogToggle.addEventListener('click', function(e) {
            e.preventDefault();
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
});

