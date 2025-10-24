document.addEventListener('DOMContentLoaded', function() {
    const dropdownBtn = document.querySelector('.footer-dropdown-btn');
    if (dropdownBtn) {
        dropdownBtn.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
        });

        document.addEventListener('click', function(e) {
            if (!e.target.closest('.footer-dropdown')) {
                dropdownBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }

    const accordionBtns = document.querySelectorAll('.footer-accordion-btn');
    accordionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
        });
    });
});

