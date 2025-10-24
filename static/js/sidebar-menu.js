(function() {
  const menuItems = document.querySelectorAll('.sidebar-menu__item.has-children');
  
  menuItems.forEach(item => {
    const link = item.querySelector('.sidebar-menu__link');
    const submenu = item.querySelector('.sidebar-menu__submenu');
    
    if (!link || !submenu) return;
    
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      
      // Якщо є підменю, запобігаємо переходу і toggle підменю
      if (submenu) {
        e.preventDefault();
        item.classList.toggle('active');
        
        // Закриваємо інші відкриті підменю
        menuItems.forEach(otherItem => {
          if (otherItem !== item) {
            otherItem.classList.remove('active');
          }
        });
      }
    });
  });
  
  // Закриття при кліку поза меню
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.sidebar-menu')) {
      menuItems.forEach(item => {
        item.classList.remove('active');
      });
    }
  });
})();

