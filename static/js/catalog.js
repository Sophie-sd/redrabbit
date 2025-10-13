/**
 * КАТАЛОГ ТОВАРІВ - JavaScript функціональність
 * Компонентний підхід з чистим кодом
 */

class CatalogManager {
    constructor() {
        this.productsGrid = document.getElementById('productsGrid');
        this.skeletonGrid = document.getElementById('skeletonGrid');
        this.productCards = [];
        this.originalCards = [];
        this.activeFilters = {};
        this.currentSort = 'default';
        
        this.init();
    }
    
    init() {
        this.cacheElements();
        this.bindEvents();
        this.loadInitialData();
        this.initMobileFilters();
        this.initWishlist();
        this.initCartActions();
        this.initPagination();
    }
    
    cacheElements() {
        // Фільтри
        this.filters = {
            priceFrom: document.getElementById('priceFrom'),
            priceTo: document.getElementById('priceTo'),
            availability: document.getElementById('availability'),
            productType: document.getElementById('productType'),
            sortBy: document.getElementById('sortBy')
        };
        
        // Кнопки та елементи управління
        this.clearFiltersBtn = document.getElementById('clearFilters');
        this.clearAllFiltersBtn = document.getElementById('clearAllFilters');
        this.activeFiltersContainer = document.getElementById('activeFilters');
        this.resultsCount = document.getElementById('resultsCount');
        this.mobileFiltersBtn = document.getElementById('mobileFiltersBtn');
        this.mobileFiltersModal = document.getElementById('mobileFiltersModal');
        
        // Кеш товарів
        this.productCards = Array.from(document.querySelectorAll('.product-card'));
        this.originalCards = [...this.productCards];
    }
    
    bindEvents() {
        // Події фільтрів
        Object.values(this.filters).forEach(element => {
            if (element) {
                if (element.type === 'number') {
                    element.addEventListener('input', this.debounce(() => this.applyFilters(), 300));
                } else {
                    element.addEventListener('change', () => this.applyFilters());
                }
            }
        });
        
        // Кнопки очищення
        if (this.clearFiltersBtn) {
            this.clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }
        
        if (this.clearAllFiltersBtn) {
            this.clearAllFiltersBtn.addEventListener('click', () => this.clearFilters());
        }
        
        // Глобальні події
        window.addEventListener('resize', this.debounce(() => this.handleResize(), 250));
    }
    
    loadInitialData() {
        // Симулюємо завантаження (якщо потрібно)
        this.showSkeleton(false);
        this.updateResultsCount(this.productCards.length, this.productCards.length);
    }
    
    applyFilters() {
        this.showSkeleton(true);
        
        // Збираємо активні фільтри
        this.collectActiveFilters();
        
        // Фільтруємо картки
        const filteredCards = this.filterProducts();
        
        // Сортуємо
        const sortedCards = this.sortProducts(filteredCards);
        
        // Відображаємо результат
        setTimeout(() => {
            this.displayProducts(sortedCards);
            this.updateActiveFilters();
            this.updateResultsCount(sortedCards.length, this.originalCards.length);
            this.showSkeleton(false);
        }, 300);
    }
    
    collectActiveFilters() {
        this.activeFilters = {};
        
        // Ціна
        const priceFrom = parseFloat(this.filters.priceFrom?.value) || 0;
        const priceTo = parseFloat(this.filters.priceTo?.value) || Infinity;
        if (priceFrom > 0 || priceTo < Infinity) {
            this.activeFilters.price = { from: priceFrom, to: priceTo };
        }
        
        // Наявність
        if (this.filters.availability?.value) {
            this.activeFilters.availability = this.filters.availability.value;
        }
        
        // Тип товару
        if (this.filters.productType?.value) {
            this.activeFilters.productType = this.filters.productType.value;
        }
        
        // Сортування
        this.currentSort = this.filters.sortBy?.value || 'default';
    }
    
    filterProducts() {
        return this.originalCards.filter(card => {
            // Фільтр за ціною
            if (this.activeFilters.price) {
                const price = parseFloat(card.dataset.salePrice);
                if (price < this.activeFilters.price.from || price > this.activeFilters.price.to) {
                    return false;
                }
            }
            
            // Фільтр за наявністю
            if (this.activeFilters.availability) {
                const inStock = card.dataset.inStock === 'True';
                const filterInStock = this.activeFilters.availability === 'in_stock';
                if (inStock !== filterInStock) {
                    return false;
                }
            }
            
            // Фільтр за типом
            if (this.activeFilters.productType) {
                const type = this.activeFilters.productType;
                const isType = card.dataset[`is${type.charAt(0).toUpperCase()}${type.slice(1)}`] === 'True';
                if (!isType) {
                    return false;
                }
            }
            
            return true;
        });
    }
    
    sortProducts(products) {
        const sorted = [...products];
        
        switch (this.currentSort) {
            case 'price_asc':
                return sorted.sort((a, b) => 
                    parseFloat(a.dataset.salePrice) - parseFloat(b.dataset.salePrice)
                );
            case 'price_desc':
                return sorted.sort((a, b) => 
                    parseFloat(b.dataset.salePrice) - parseFloat(a.dataset.salePrice)
                );
            case 'name':
                return sorted.sort((a, b) => 
                    a.dataset.name.localeCompare(b.dataset.name, 'uk')
                );
            case 'new':
                return sorted.sort((a, b) => 
                    (b.dataset.isNew === 'True' ? 1 : 0) - (a.dataset.isNew === 'True' ? 1 : 0)
                );
            case 'popular':
                return sorted.sort((a, b) => 
                    (b.dataset.isTop === 'True' ? 1 : 0) - (a.dataset.isTop === 'True' ? 1 : 0)
                );
            default:
                return sorted;
        }
    }
    
    displayProducts(products) {
        // Приховуємо всі картки
        this.originalCards.forEach(card => {
            card.style.display = 'none';
        });
        
        // Показуємо відфільтровані картки
        products.forEach(card => {
            card.style.display = 'flex';
            this.productsGrid.appendChild(card);
        });
        
        // Показуємо порожній стан якщо немає товарів
        this.toggleEmptyState(products.length === 0);
    }
    
    updateActiveFilters() {
        if (!this.activeFiltersContainer) return;
        
        const hasFilters = Object.keys(this.activeFilters).length > 0 || this.currentSort !== 'default';
        
        if (!hasFilters) {
            this.activeFiltersContainer.style.display = 'none';
            return;
        }
        
        this.activeFiltersContainer.style.display = 'block';
        this.activeFiltersContainer.innerHTML = '';
        
        // Додаємо чіпи для активних фільтрів
        Object.entries(this.activeFilters).forEach(([key, value]) => {
            const chip = this.createFilterChip(key, value);
            if (chip) {
                this.activeFiltersContainer.appendChild(chip);
            }
        });
        
        // Додаємо чіп для сортування
        if (this.currentSort !== 'default') {
            const sortText = this.filters.sortBy?.options[this.filters.sortBy.selectedIndex]?.text;
            if (sortText) {
                const chip = this.createFilterChip('sort', sortText);
                if (chip) {
                    this.activeFiltersContainer.appendChild(chip);
                }
            }
        }
    }
    
    createFilterChip(key, value) {
        const chip = document.createElement('div');
        chip.className = 'filter-chip';
        
        let text = '';
        switch (key) {
            case 'price':
                text = `Ціна: ${value.from || 0} - ${value.to === Infinity ? '∞' : value.to} ₴`;
                break;
            case 'availability':
                text = value === 'in_stock' ? 'В наявності' : 'Під замовлення';
                break;
            case 'productType':
                const typeMap = {
                    'sale': 'Акційні',
                    'new': 'Новинки',
                    'top': 'Хіти продажу'
                };
                text = typeMap[value] || value;
                break;
            case 'sort':
                text = `Сортування: ${value}`;
                break;
        }
        
        if (!text) return null;
        
        chip.innerHTML = `
            <span>${text}</span>
            <button type="button" class="filter-chip__remove" aria-label="Видалити фільтр">
                ✕
            </button>
        `;
        
        chip.querySelector('.filter-chip__remove').addEventListener('click', () => {
            this.removeFilter(key);
        });
        
        return chip;
    }
    
    removeFilter(key) {
        switch (key) {
            case 'price':
                if (this.filters.priceFrom) this.filters.priceFrom.value = '';
                if (this.filters.priceTo) this.filters.priceTo.value = '';
                break;
            case 'availability':
                if (this.filters.availability) this.filters.availability.value = '';
                break;
            case 'productType':
                if (this.filters.productType) this.filters.productType.value = '';
                break;
            case 'sort':
                if (this.filters.sortBy) this.filters.sortBy.value = 'default';
                break;
        }
        
        this.applyFilters();
    }
    
    clearFilters() {
        Object.values(this.filters).forEach(element => {
            if (element) {
                element.value = element.type === 'select-one' ? '' : '';
            }
        });
        
        if (this.filters.sortBy) {
            this.filters.sortBy.value = 'default';
        }
        
        this.applyFilters();
    }
    
    updateResultsCount(filtered, total) {
        if (this.resultsCount) {
            this.resultsCount.textContent = `Показано ${filtered} з ${total} товарів`;
        }
    }
    
    toggleEmptyState(show) {
        const emptyState = document.querySelector('.empty-state');
        if (emptyState) {
            emptyState.style.display = show ? 'flex' : 'none';
        }
        
        if (this.productsGrid) {
            this.productsGrid.style.display = show ? 'none' : 'grid';
        }
    }
    
    showSkeleton(show) {
        if (this.skeletonGrid) {
            this.skeletonGrid.style.display = show ? 'grid' : 'none';
        }
        
        if (this.productsGrid) {
            this.productsGrid.style.display = show ? 'none' : 'grid';
        }
    }
    
    // Мобільні фільтри
    initMobileFilters() {
        if (!this.mobileFiltersBtn || !this.mobileFiltersModal) return;
        
        const modalContent = this.mobileFiltersModal.querySelector('.modal-filters__content');
        const modalBody = this.mobileFiltersModal.querySelector('.modal-filters__body');
        const closeBtn = this.mobileFiltersModal.querySelector('.modal-filters__close');
        const backdrop = this.mobileFiltersModal.querySelector('.modal-filters__backdrop');
        const applyBtn = this.mobileFiltersModal.querySelector('.modal-filters__apply');
        const clearBtn = this.mobileFiltersModal.querySelector('.modal-filters__clear');
        
        // Відкриття модального вікна
        this.mobileFiltersBtn.addEventListener('click', () => {
            this.copyFiltersToModal();
            this.mobileFiltersModal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            
            // Фокус на першому елементі
            const firstInput = modalBody.querySelector('input, select');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        });
        
        // Закриття модального вікна
        const closeModal = () => {
            this.mobileFiltersModal.style.display = 'none';
            document.body.style.overflow = '';
        };
        
        closeBtn?.addEventListener('click', closeModal);
        backdrop?.addEventListener('click', closeModal);
        
        // Обробка Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.mobileFiltersModal.style.display === 'flex') {
                closeModal();
            }
        });
        
        // Застосування фільтрів
        applyBtn?.addEventListener('click', () => {
            this.copyFiltersFromModal();
            this.applyFilters();
            closeModal();
        });
        
        // Очищення фільтрів
        clearBtn?.addEventListener('click', () => {
            modalBody.querySelectorAll('input, select').forEach(element => {
                element.value = '';
            });
        });
    }
    
    copyFiltersToModal() {
        const modalBody = this.mobileFiltersModal.querySelector('.modal-filters__body');
        const filtersLeft = document.querySelector('.filters-bar__left');
        
        if (filtersLeft && modalBody) {
            modalBody.innerHTML = filtersLeft.innerHTML;
            
            // Копіюємо значення фільтрів
            modalBody.querySelectorAll('input, select').forEach(element => {
                const originalElement = document.getElementById(element.id);
                if (originalElement) {
                    element.value = originalElement.value;
                }
            });
        }
    }
    
    copyFiltersFromModal() {
        const modalBody = this.mobileFiltersModal.querySelector('.modal-filters__body');
        
        modalBody.querySelectorAll('input, select').forEach(element => {
            const originalElement = document.getElementById(element.id);
            if (originalElement) {
                originalElement.value = element.value;
            }
        });
    }
    
    // Список бажань
    initWishlist() {
        const wishlistBtns = document.querySelectorAll('.product-card__wishlist');
        
        wishlistBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const productId = btn.dataset.productId;
                const isActive = btn.classList.contains('product-card__wishlist--active');
                
                this.toggleWishlist(btn, productId, isActive);
            });
        });
    }
    
    async toggleWishlist(btn, productId, isActive) {
        try {
            // Анімація
            btn.style.transform = 'scale(1.3)';
            setTimeout(() => {
                btn.style.transform = 'scale(1)';
            }, 200);
            
            const url = isActive ? '/wishlist/remove/' : '/wishlist/add/';
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: `product_id=${productId}`
            });
            
            const data = await response.json();
            
            if (data.success) {
                btn.classList.toggle('product-card__wishlist--active');
                const icon = btn.querySelector('.product-card__wishlist-icon');
                if (icon) {
                    icon.textContent = isActive ? '♡' : '♥';
                }
                
                this.showToast(isActive ? 'Видалено з обраного' : 'Додано до обраного');
            }
        } catch (error) {
            console.error('Wishlist error:', error);
            this.showToast('Помилка. Спробуйте ще раз', 'error');
        }
    }
    
    // Дії кошика
    initCartActions() {
        const addToCartBtns = document.querySelectorAll('.product-card__add-cart');
        
        addToCartBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                
                if (btn.disabled) return;
                
                const productId = btn.dataset.productId;
                this.addToCart(btn, productId);
            });
        });
    }
    
    async addToCart(btn, productId) {
        const originalText = btn.textContent;
        
        try {
            btn.classList.add('product-card__add-cart--loading');
            btn.textContent = 'Додається...';
            btn.disabled = true;
            
            const response = await fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: `product_id=${productId}&quantity=1`
            });
            
            const data = await response.json();
            
            if (data.success) {
                btn.classList.add('product-card__add-cart--added');
                btn.textContent = '✓ Додано';
                
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.classList.remove('product-card__add-cart--added');
                    btn.disabled = false;
                }, 2000);
                
                this.updateCartCount(data.cart_count);
                this.showToast('Товар додано до кошика');
            }
        } catch (error) {
            console.error('Cart error:', error);
            btn.textContent = originalText;
            btn.disabled = false;
            this.showToast('Помилка додавання до кошика', 'error');
        } finally {
            btn.classList.remove('product-card__add-cart--loading');
        }
    }
    
    // Пагінація
    initPagination() {
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                this.loadMoreProducts(loadMoreBtn);
            });
        }
    }
    
    async loadMoreProducts(btn) {
        const nextPage = btn.dataset.nextPage;
        const originalText = btn.textContent;
        
        try {
            btn.textContent = 'Завантаження...';
            btn.disabled = true;
            
            const url = new URL(window.location);
            url.searchParams.set('page', nextPage);
            
            const response = await fetch(url);
            const html = await response.text();
            
            // Парсимо нові товари (тут буде складніша логіка в реальному проекті)
            this.showToast('Більше товарів завантажено');
            
        } catch (error) {
            console.error('Load more error:', error);
            btn.textContent = originalText;
            btn.disabled = false;
            this.showToast('Помилка завантаження', 'error');
        }
    }
    
    // Утилітарні методи
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    updateCartCount(count) {
        const cartCountElements = document.querySelectorAll('.cart-count, [data-cart-count]');
        cartCountElements.forEach(element => {
            element.textContent = count;
        });
    }
    
    showToast(message, type = 'success') {
        // Створюємо toast елемент
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.textContent = message;
        
        // Додаємо стилі
        Object.assign(toast.style, {
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            padding: '12px 20px',
            backgroundColor: type === 'error' ? '#f44336' : '#4caf50',
            color: 'white',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
            zIndex: '10000',
            fontSize: '14px',
            fontWeight: '500',
            opacity: '0',
            transform: 'translateY(20px)',
            transition: 'all 0.3s ease'
        });
        
        document.body.appendChild(toast);
        
        // Показуємо з анімацією
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 100);
        
        // Приховуємо через 3 секунди
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    handleResize() {
        // Обробка зміни розміру вікна
        if (window.innerWidth >= 600) {
            // Закриваємо мобільну модалку на більших екранах
            if (this.mobileFiltersModal.style.display === 'flex') {
                this.mobileFiltersModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        }
    }
}

// Ініціалізація після завантаження DOM
document.addEventListener('DOMContentLoaded', () => {
    const catalog = new CatalogManager();
    
    // Експортуємо в глобальний простір для налагодження
    window.catalog = catalog;
});
