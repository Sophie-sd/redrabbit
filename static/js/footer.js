document.addEventListener('DOMContentLoaded', function() {
    const catalogToggle = document.getElementById('footerCatalogToggle');
    const catalogDropdown = document.getElementById('footerCatalogDropdown');
    
    if (catalogToggle && catalogDropdown) {
        catalogToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            catalogDropdown.classList.toggle('active');
        });
    }
    
    const accordionToggles = document.querySelectorAll('[data-accordion-toggle]');
    
    accordionToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const accordionItem = this.closest('.mobile-accordion-item');
            const isActive = accordionItem.classList.contains('active');
            
            document.querySelectorAll('.mobile-accordion-item').forEach(function(item) {
                item.classList.remove('active');
            });
            
            if (!isActive) {
                accordionItem.classList.add('active');
            }
        });
    });
    
    const footerSubscribeForm = document.getElementById('footerSubscribeForm');
    if (footerSubscribeForm) {
        footerSubscribeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Дякуємо за підписку!');
            this.reset();
        });
    }
    
    const mobileSubscribeForm = document.getElementById('mobileSubscribeForm');
    if (mobileSubscribeForm) {
        mobileSubscribeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Дякуємо за підписку!');
            this.reset();
        });
    }
});

