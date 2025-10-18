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
        .then(res => res.json())
        .then(data => {
          if (data.results && data.results.length > 0) {
            autocomplete.innerHTML = data.results.map(item => `
              <a href="${item.url}" class="autocomplete-item">
                ${item.image ? `<img src="${item.image}" alt="${item.name}" loading="lazy">` : ''}
                <span class="autocomplete-name">${item.name}</span>
                <span class="autocomplete-price">${item.price} ₴</span>
              </a>
            `).join('');
            autocomplete.classList.add('active');
          } else {
            autocomplete.innerHTML = '<div class="autocomplete-empty">Нічого не знайдено</div>';
            autocomplete.classList.add('active');
          }
        })
        .catch(() => {
          autocomplete.innerHTML = '<div class="autocomplete-empty">Помилка пошуку</div>';
          autocomplete.classList.add('active');
        });
    }, 300);
  });
  
  document.addEventListener('click', function(e) {
    if (!searchInput.contains(e.target) && !autocomplete.contains(e.target)) {
      autocomplete.classList.remove('active');
    }
  });
})();

