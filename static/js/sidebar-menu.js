document.addEventListener('DOMContentLoaded', () => {
    const sidebarToggles = document.querySelectorAll('.sidebar-menu__toggle');
    
    sidebarToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const item = toggle.closest('.sidebar-menu__item');
            item.classList.toggle('open');
        });
    });
});
