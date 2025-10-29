(function() {
  const searchInput = document.getElementById('searchInput');
  const autocomplete = document.getElementById('searchAutocomplete');
  let debounceTimer;
  let currentRequest = null; // Для відміни попередніх запитів
  let lastQuery = ''; // Зберігаємо останній запит
  
  if (!searchInput || !autocomplete) return;
  
  searchInput.addEventListener('input', function() {
    const query = this.value.trim();
    
    clearTimeout(debounceTimer);
    
    // Скасовуємо попередній запит якщо він ще виконується
    if (currentRequest) {
      currentRequest.abort();
      currentRequest = null;
    }
    
    if (query.length < 2) {
      autocomplete.innerHTML = '';
      autocomplete.classList.remove('active');
      lastQuery = '';
      return;
    }
    
    debounceTimer = setTimeout(() => {
      // Зберігаємо поточний запит для перевірки актуальності
      const queryToSearch = query;
      lastQuery = queryToSearch;
      
      // Створюємо AbortController для можливості скасування
      const controller = new AbortController();
      currentRequest = controller;
      
      fetch(`/api/search/autocomplete/?q=${encodeURIComponent(queryToSearch)}`, {
        signal: controller.signal
      })
        .then(res => {
          if (!res.ok) {
            throw new Error('Network response was not ok');
          }
          return res.json();
        })
        .then(data => {
          // Перевіряємо чи запит ще актуальний
          if (queryToSearch !== lastQuery) {
            console.log('Ignoring outdated response for:', queryToSearch);
            return;
          }
          
          currentRequest = null;
          
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
          currentRequest = null;
          
          // Ігноруємо помилки від скасованих запитів
          if (err.name === 'AbortError') {
            console.log('Search request aborted');
            return;
          }
          
          console.error('Search error:', err);
          
          // Показуємо помилку тільки якщо запит ще актуальний
          if (queryToSearch === lastQuery) {
            autocomplete.innerHTML = '<div class="autocomplete-empty">Помилка пошуку</div>';
            autocomplete.classList.add('active');
          }
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

