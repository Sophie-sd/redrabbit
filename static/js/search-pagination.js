/**
 * Динамічна пагінація для сторінки пошуку
 * Завантажує товари в реальному часі та оновлює лічильник
 */

(function() {
  // Перевіряємо чи є необхідні глобальні змінні
  if (!window.searchQuery || window.initialCount === undefined) {
    console.log('Search pagination: not initialized');
    return;
  }

  const query = window.searchQuery;
  const productsGrid = document.getElementById('searchProductsGrid');
  const resultsCount = document.getElementById('resultsCount');
  const searchLoading = document.getElementById('searchLoading');
  const searchPagination = document.getElementById('searchPagination');
  
  if (!productsGrid || !resultsCount) {
    console.error('Search pagination: required elements not found');
    return;
  }

  // Стан пагінації
  let currentPage = 1;
  let totalPages = 1;
  let totalCount = window.initialCount;
  let isLoading = false;
  let allProductsLoaded = false;

  /**
   * Оновлює лічильник результатів
   */
  function updateResultsCount(count) {
    totalCount = count;
    const plural = count % 10 === 1 && count % 100 !== 11 ? '' :
                   (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) ? 'и' : 'ів';
    resultsCount.textContent = `Знайдено ${count} товар${plural}`;
  }

  /**
   * Створює HTML для картки товару
   */
  function createProductCard(product) {
    const imageHtml = product.image 
      ? `<img src="${product.image}" alt="${product.name}" loading="lazy">`
      : '<div class="product-card__placeholder">📦</div>';
    
    // Бейджі
    let badgesHtml = '';
    if (product.is_sale) {
      badgesHtml += '<span class="badge badge-sale">АКЦІЯ</span>';
    }
    if (product.is_top) {
      badgesHtml += '<span class="badge badge-top">ТОП</span>';
    }
    if (product.is_new) {
      badgesHtml += '<span class="badge badge-new">Новинка</span>';
    }

    return `
      <article class="product-card" data-product-id="${product.id}">
        <a href="${product.url}" class="product-card__link">
          <div class="product-card__image-wrapper">
            ${imageHtml}
            ${badgesHtml ? `<div class="product-card__badges">${badgesHtml}</div>` : ''}
          </div>
          <div class="product-card__content">
            <h3 class="product-card__name">${product.name}</h3>
            <div class="product-card__price">${product.price} ₴</div>
          </div>
        </a>
        <div class="product-card__actions">
          <button class="btn btn-primary btn-block add-to-cart" data-product-id="${product.id}">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
              <path d="M9 2L6 6H3L3 22H21L21 6H18L15 2H9Z" stroke="currentColor" stroke-width="2"/>
            </svg>
            Купити
          </button>
        </div>
      </article>
    `;
  }

  /**
   * Завантажує товари для вказаної сторінки
   */
  async function loadPage(page) {
    if (isLoading || allProductsLoaded) return;
    
    isLoading = true;
    if (searchLoading) searchLoading.style.display = 'block';

    try {
      const response = await fetch(`/api/search/paginated/?q=${encodeURIComponent(query)}&page=${page}&per_page=20`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Оновлюємо лічильник
      updateResultsCount(data.total_count);
      
      // Додаємо товари до сітки
      if (data.products && data.products.length > 0) {
        data.products.forEach(product => {
          const cardHtml = createProductCard(product);
          productsGrid.insertAdjacentHTML('beforeend', cardHtml);
        });
      }
      
      // Оновлюємо стан пагінації
      currentPage = data.current_page;
      totalPages = data.total_pages;
      
      // Якщо це остання сторінка
      if (!data.has_next) {
        allProductsLoaded = true;
      }
      
      // Оновлюємо пагінацію
      renderPagination(data);
      
    } catch (error) {
      console.error('Error loading search results:', error);
      resultsCount.textContent = 'Помилка завантаження результатів';
    } finally {
      isLoading = false;
      if (searchLoading) searchLoading.style.display = 'none';
    }
  }

  /**
   * Створює HTML для пагінації
   */
  function renderPagination(data) {
    if (!searchPagination) return;
    
    if (data.total_pages <= 1) {
      searchPagination.innerHTML = '';
      return;
    }

    let paginationHtml = '<div class="pagination">';
    
    // Кнопка "Попередня"
    if (data.has_prev) {
      paginationHtml += `<button class="pagination__btn pagination__btn--prev" data-page="${data.current_page - 1}">
        <svg viewBox="0 0 24 24" width="16" height="16">
          <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        Назад
      </button>`;
    }
    
    // Номери сторінок
    paginationHtml += '<div class="pagination__numbers">';
    
    const maxVisible = 7;
    let startPage = Math.max(1, data.current_page - Math.floor(maxVisible / 2));
    let endPage = Math.min(data.total_pages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    // Перша сторінка
    if (startPage > 1) {
      paginationHtml += `<button class="pagination__number" data-page="1">1</button>`;
      if (startPage > 2) {
        paginationHtml += '<span class="pagination__ellipsis">...</span>';
      }
    }
    
    // Середні сторінки
    for (let i = startPage; i <= endPage; i++) {
      const isActive = i === data.current_page ? 'pagination__number--active' : '';
      paginationHtml += `<button class="pagination__number ${isActive}" data-page="${i}">${i}</button>`;
    }
    
    // Остання сторінка
    if (endPage < data.total_pages) {
      if (endPage < data.total_pages - 1) {
        paginationHtml += '<span class="pagination__ellipsis">...</span>';
      }
      paginationHtml += `<button class="pagination__number" data-page="${data.total_pages}">${data.total_pages}</button>`;
    }
    
    paginationHtml += '</div>';
    
    // Кнопка "Наступна"
    if (data.has_next) {
      paginationHtml += `<button class="pagination__btn pagination__btn--next" data-page="${data.current_page + 1}">
        Далі
        <svg viewBox="0 0 24 24" width="16" height="16">
          <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
      </button>`;
    }
    
    paginationHtml += '</div>';
    
    searchPagination.innerHTML = paginationHtml;
    
    // Додаємо обробники подій
    searchPagination.querySelectorAll('[data-page]').forEach(btn => {
      btn.addEventListener('click', function() {
        const page = parseInt(this.getAttribute('data-page'));
        if (page !== currentPage) {
          // Прокручуємо до початку результатів
          const searchResults = document.querySelector('.search-results');
          if (searchResults) {
            searchResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
          
          // Очищаємо сітку та завантажуємо нову сторінку
          const initialCards = productsGrid.querySelectorAll('.product-card');
          // Залишаємо тільки перші 5 карток (initial load)
          if (page === 1) {
            // Для першої сторінки залишаємо початкові 5
            Array.from(initialCards).slice(5).forEach(card => card.remove());
            currentPage = 0;
            allProductsLoaded = false;
          } else {
            // Для інших сторінок очищаємо все крім перших 5
            Array.from(initialCards).slice(5).forEach(card => card.remove());
            currentPage = 0;
            allProductsLoaded = false;
            // Завантажуємо всі сторінки до потрібної
            loadMultiplePages(page);
            return;
          }
          
          loadPage(page);
        }
      });
    });
  }

  /**
   * Завантажує кілька сторінок підряд
   */
  async function loadMultiplePages(targetPage) {
    for (let page = 2; page <= targetPage; page++) {
      await loadPage(page);
    }
  }

  /**
   * Ініціалізація - завантажуємо решту товарів
   */
  function init() {
    // Якщо є початкові товари, показуємо їх кількість
    if (window.initialCount > 0) {
      updateResultsCount(window.initialCount);
    }
    
    // Автоматично завантажуємо наступні сторінки
    setTimeout(() => {
      loadPage(2); // Завантажуємо другу сторінку (перші 5 вже є)
    }, 100);
  }

  // Запускаємо ініціалізацію
  init();
})();

