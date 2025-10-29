(function() {
  const searchInput = document.getElementById('searchInput');
  const autocomplete = document.getElementById('searchAutocomplete');
  let debounceTimer;
  
  if (!searchInput || !autocomplete) return;
  
  searchInput.addEventListener('input', function() {
    const query = this.value.trim();
    
    clearTimeout(debounceTimer);
    
    if (query.length < 2) {
      autocomplete.innerHTML = '';
      autocomplete.classList.remove('active');
      return;
    }
    
    debounceTimer = setTimeout(() => {
      fetch(`/api/search/autocomplete/?q=${encodeURIComponent(query)}`)
        .then(res => {
          if (!res.ok) {
            throw new Error('Network response was not ok');
          }
          return res.json();
        })
        .then(data => {
          if (data.results && data.results.length > 0) {
            autocomplete.innerHTML = data.results.map(item => {
              const imageHtml = item.image ? `<img src="${item.image}" alt="${item.name}" loading="lazy">` : '<div class="autocomplete-placeholder">📦</div>';
              return `
                <a href="${item.url}" class="autocomplete-item" data-product-url="${item.url}">
                  ${imageHtml}
                  <span class="autocomplete-name">${item.name}</span>
                  <span class="autocomplete-price">${item.price} ₴</span>
                </a>
              `;
            }).join('');
            autocomplete.classList.add('active');
            
            // Додаємо event listener для кожного елемента
            autocomplete.querySelectorAll('.autocomplete-item').forEach(item => {
              item.addEventListener('click', function(e) {
                e.preventDefault();
                const url = this.getAttribute('data-product-url');
                if (url) {
                  window.location.href = url;
                }
              });
            });
          } else {
            autocomplete.innerHTML = '<div class="autocomplete-empty">Нічого не знайдено</div>';
            autocomplete.classList.add('active');
          }
        })
        .catch(err => {
          console.error('Search error:', err);
          autocomplete.innerHTML = '<div class="autocomplete-empty">Помилка пошуку</div>';
          autocomplete.classList.add('active');
        });
    }, 300);
  });
  
  // Закриття autocomplete при кліку поза ним
  document.addEventListener('click', function(e) {
    if (!searchInput.contains(e.target) && !autocomplete.contains(e.target)) {
      autocomplete.classList.remove('active');
    }
  });
  
  // Закриття autocomplete при натисканні Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      autocomplete.classList.remove('active');
    }
  });
})();

