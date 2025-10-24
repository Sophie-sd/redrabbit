(function() {
  const menuItems = document.querySelectorAll('.sidebar-menu__item.has-children');
  
  menuItems.forEach(item => {
    const toggle = item.querySelector('.sidebar-menu__toggle');
    const submenu = item.querySelector('.sidebar-menu__submenu');
    
    if (!toggle || !submenu) return;
    
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const isExpanded = item.classList.contains('expanded');
      
      menuItems.forEach(otherItem => {
        otherItem.classList.remove('expanded');
      });
      
      if (!isExpanded) {
        item.classList.add('expanded');
      }
    });
  });
  
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.sidebar-menu')) {
      menuItems.forEach(item => {
        item.classList.remove('expanded');
      });
    }
  });
})();

