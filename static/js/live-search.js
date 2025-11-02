(function() {
  const searchInput = document.getElementById('searchInput');
  const autocomplete = document.getElementById('searchAutocomplete');
  let debounceTimer;
  let currentRequest = null;
  let lastQuery = '';
  const searchCache = new Map(); // Кеш результатів пошуку
  const CACHE_DURATION = 5 * 60 * 1000; // 5 хвилин
  
  if (!searchInput || !autocomplete) return;
  
  // Очищення застарілих елементів кешу
  function cleanCache() {
    const now = Date.now();
    for (const [key, value] of searchCache.entries()) {
      if (now - value.timestamp > CACHE_DURATION) {
        searchCache.delete(key);
      }
    }
  }
  
  searchInput.addEventListener('input', function() {
    const query = this.value.trim();
    
    clearTimeout(debounceTimer);
    
    // Скасовуємо попередній запит
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
      const queryToSearch = query;
      lastQuery = queryToSearch;
      
      // Перевіряємо кеш
      const cacheKey = queryToSearch.toLowerCase();
      const cached = searchCache.get(cacheKey);
      
      if (cached && (Date.now() - cached.timestamp < CACHE_DURATION)) {
        displayResults(cached.data);
        return;
      }
      
      // Створюємо AbortController
      const controller = new AbortController();
      currentRequest = controller;
      
      fetch(`/api/search/autocomplete/?q=${encodeURIComponent(queryToSearch)}`, {
        signal: controller.signal
      })
        .then(res => {
          if (!res.ok) throw new Error('Network response was not ok');
          return res.json();
        })
        .then(data => {
          if (queryToSearch !== lastQuery) return;
          
          currentRequest = null;
          
          // Зберігаємо в кеш
          searchCache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
          });
          
          // Очищаємо застарілі елементи кешу
          if (searchCache.size > 50) {
            cleanCache();
          }
          
          displayResults(data);
        })
        .catch(err => {
          currentRequest = null;
          
          if (err.name === 'AbortError') return;
          
          console.error('Search error:', err);
          
          if (queryToSearch === lastQuery) {
            autocomplete.innerHTML = '<div class="autocomplete-empty">Помилка пошуку</div>';
            autocomplete.classList.add('active');
          }
        });
    }, 500); // Збільшено з 300ms до 500ms
  });
  
  function displayResults(data) {
    if (data.results && data.results.length > 0) {
      autocomplete.innerHTML = data.results.map(item => {
        const imageHtml = item.image 
          ? `<img src="${item.image}" alt="${item.name}" loading="lazy" width="50" height="50">` 
          : '<div class="autocomplete-placeholder">📦</div>';
        return `
          <a href="${item.url}" class="autocomplete-item" data-product-url="${item.url}">
            ${imageHtml}
            <span class="autocomplete-name">${item.name}</span>
            <span class="autocomplete-price">${item.price} ₴</span>
          </a>
        `;
      }).join('');
      autocomplete.classList.add('active');
      
      autocomplete.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', function(e) {
          e.preventDefault();
          const url = this.getAttribute('data-product-url');
          if (url) window.location.href = url;
        });
      });
    } else {
      autocomplete.innerHTML = '<div class="autocomplete-empty">Нічого не знайдено</div>';
      autocomplete.classList.add('active');
    }
  }
  
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

