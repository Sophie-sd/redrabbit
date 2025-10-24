class CatalogManager {
    constructor() {
        this.productsGrid = document.getElementById('productsGrid');
        this.skeletonGrid = document.getElementById('skeletonGrid');
        this.productCards = [];
        this.originalCards = [];
        this.activeFilters = {
            price: { min: 0, max: Infinity },
            availability: [],
            brands: [],
            power: [],
            waterproof: [],
            vibration: [],
            types: []
        };
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
        this.initFiltersToggle();
    }
    
    cacheElements() {
        this.filters = {
            priceMin: document.getElementById('priceMin'),
            priceMax: document.getElementById('priceMax'),
            availability: document.querySelectorAll('input[name="availability"]'),
            brands: document.querySelectorAll('input[name="brand"]'),
            power: document.querySelectorAll('input[name="power"]'),
            waterproof: document.querySelectorAll('input[name="waterproof"]'),
            vibration: document.querySelectorAll('input[name="vibration"]'),
            types: document.querySelectorAll('input[name="type"]')
        };
        
        this.clearFiltersBtn = document.getElementById('clearAllFilters');
        this.applyFiltersBtn = document.getElementById('applyFiltersBtn');
        this.activeFiltersContainer = document.getElementById('activeFilters');
        this.resultsCount = document.getElementById('resultsCount');
        this.mobileFiltersBtn = document.getElementById('mobileFiltersBtn');
        this.mobileFiltersModal = document.getElementById('mobileFiltersModal');
        this.sortSelectBtn = document.getElementById('sortSelectBtn');
        this.sortDropdown = document.getElementById('sortDropdown');
        this.mobileFiltersClose = document.getElementById('mobileFiltersClose');
        
        this.productCards = Array.from(document.querySelectorAll('.product-card'));
        this.originalCards = [...this.productCards];
    }
    
    bindEvents() {
        if (this.filters.priceMin) {
            this.filters.priceMin.addEventListener('input', this.debounce(() => this.applyFilters(), 500));
        }
        if (this.filters.priceMax) {
            this.filters.priceMax.addEventListener('input', this.debounce(() => this.applyFilters(), 500));
        }
        
        const allCheckboxes = [
            ...this.filters.availability,
            ...this.filters.brands,
            ...this.filters.power,
            ...this.filters.waterproof,
            ...this.filters.vibration,
            ...this.filters.types
        ];
        
        allCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                if (!this.isInMobileModal(checkbox)) {
                    this.applyFilters();
                }
            });
        });
        
        if (this.clearFiltersBtn) {
            this.clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }
        
        if (this.applyFiltersBtn) {
            this.applyFiltersBtn.addEventListener('click', () => {
                this.applyFilters();
                const filtersToggle = document.getElementById('filtersToggle');
                const filtersContent = document.getElementById('filtersContent');
                if (filtersToggle && filtersContent) {
                    filtersToggle.classList.remove('active');
                    filtersContent.classList.remove('active');
                }
            });
        }
        
        if (this.sortSelectBtn && this.sortDropdown) {
            this.sortSelectBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.sortDropdown.classList.toggle('hidden');
                this.sortSelectBtn.classList.toggle('active');
            });
            
            this.sortDropdown.querySelectorAll('.sort-option').forEach(option => {
                option.addEventListener('click', () => {
                    const value = option.dataset.value;
                    this.currentSort = value;
                    this.sortSelectBtn.querySelector('.sort-select-text').textContent = option.textContent;
                    this.sortDropdown.classList.add('hidden');
                    this.sortSelectBtn.classList.remove('active');
                    this.applyFilters();
                });
            });
            
            document.addEventListener('click', (e) => {
                if (!this.sortSelectBtn.contains(e.target) && !this.sortDropdown.contains(e.target)) {
                    this.sortDropdown.classList.add('hidden');
                    this.sortSelectBtn.classList.remove('active');
                }
            });
        }
        
        this.desktopSortBtn = document.getElementById('desktopSortBtn');
        this.desktopSortDropdown = document.getElementById('desktopSortDropdown');
        
        if (this.desktopSortBtn && this.desktopSortDropdown) {
            this.desktopSortBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.desktopSortDropdown.classList.toggle('hidden');
                this.desktopSortBtn.classList.toggle('active');
            });
            
            this.desktopSortDropdown.querySelectorAll('.sort-option').forEach(option => {
                option.addEventListener('click', () => {
                    const value = option.dataset.value;
                    this.currentSort = value;
                    this.desktopSortBtn.querySelector('.sort-text').textContent = option.textContent;
                    this.desktopSortDropdown.classList.add('hidden');
                    this.desktopSortBtn.classList.remove('active');
                    this.applyFilters();
                });
            });
            
        document.addEventListener('click', (e) => {
                if (!this.desktopSortBtn.contains(e.target) && !this.desktopSortDropdown.contains(e.target)) {
                    this.desktopSortDropdown.classList.add('hidden');
                    this.desktopSortBtn.classList.remove('active');
                }
            });
        }
    }
    
    loadInitialData() {
        this.productCards = Array.from(document.querySelectorAll('.product-card'));
        this.originalCards = [...this.productCards];
        this.updateResultsCount(this.productCards.length, this.productCards.length);
    }
    
    applyFilters() {
        this.showSkeleton(true);
        
        this.collectActiveFilters();
        
        const filteredCards = this.filterProducts();
        
        const sortedCards = this.sortProducts(filteredCards);
        
        setTimeout(() => {
            this.displayProducts(sortedCards);
            this.updateActiveFiltersDisplay();
            this.updateResultsCount(sortedCards.length, this.originalCards.length);
            this.showSkeleton(false);
        }, 300);
    }
    
    collectActiveFilters() {
        const priceMin = parseFloat(this.filters.priceMin?.value) || 0;
        const priceMax = parseFloat(this.filters.priceMax?.value) || Infinity;
        this.activeFilters.price = { min: priceMin, max: priceMax };
        
        this.activeFilters.availability = Array.from(this.filters.availability)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        this.activeFilters.brands = Array.from(this.filters.brands)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        this.activeFilters.power = Array.from(this.filters.power)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        this.activeFilters.waterproof = Array.from(this.filters.waterproof)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        this.activeFilters.vibration = Array.from(this.filters.vibration)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        this.activeFilters.types = Array.from(this.filters.types)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
    }
    
    filterProducts() {
        return this.originalCards.filter(card => {
                const price = parseFloat(card.dataset.salePrice);
            if (price < this.activeFilters.price.min || price > this.activeFilters.price.max) {
                return false;
            }
            
            if (this.activeFilters.availability.length > 0) {
                const inStock = card.dataset.inStock === 'True';
                const hasInStock = this.activeFilters.availability.includes('in_stock');
                const hasOutOfStock = this.activeFilters.availability.includes('out_of_stock');
                
                if (hasInStock && !inStock) return false;
                if (hasOutOfStock && inStock) return false;
            }
            
            if (this.activeFilters.brands.length > 0) {
                const vendor = card.dataset.vendor || '';
                if (!this.activeFilters.brands.includes(vendor)) {
                    return false;
                }
            }
            
            if (this.activeFilters.power.length > 0) {
                const power = card.dataset.power || '';
                if (!this.activeFilters.power.includes(power)) {
                    return false;
                }
            }
            
            if (this.activeFilters.waterproof.length > 0) {
                const waterproof = card.dataset.waterproof || '';
                if (!this.activeFilters.waterproof.includes(waterproof)) {
                    return false;
                }
            }
            
            if (this.activeFilters.vibration.length > 0) {
                const vibration = card.dataset.vibration || '';
                if (!this.activeFilters.vibration.includes(vibration)) {
                    return false;
                }
            }
            
            if (this.activeFilters.types.length > 0) {
                const hasNew = card.dataset.isNew === 'True';
                const hasSale = card.dataset.isSale === 'True';
                const hasTop = card.dataset.isTop === 'True';
                
                const matchTypes = this.activeFilters.types.some(type => {
                    if (type === 'new') return hasNew;
                    if (type === 'sale') return hasSale;
                    if (type === 'top') return hasTop;
                    return false;
                });
                
                if (!matchTypes) return false;
            }
            
            return true;
        });
    }
    
    sortProducts(cards) {
        const sorted = [...cards];
        
        switch (this.currentSort) {
            case 'price_asc':
                sorted.sort((a, b) => parseFloat(a.dataset.salePrice) - parseFloat(b.dataset.salePrice));
                break;
            case 'price_desc':
                sorted.sort((a, b) => parseFloat(b.dataset.salePrice) - parseFloat(a.dataset.salePrice));
                break;
            case 'name':
                sorted.sort((a, b) => a.dataset.name.localeCompare(b.dataset.name));
                break;
            case 'popular':
                sorted.sort((a, b) => {
                    const aTop = a.dataset.isTop === 'True' ? 1 : 0;
                    const bTop = b.dataset.isTop === 'True' ? 1 : 0;
                    return bTop - aTop;
                });
                break;
            case 'new':
                sorted.sort((a, b) => {
                    const aNew = a.dataset.isNew === 'True' ? 1 : 0;
                    const bNew = b.dataset.isNew === 'True' ? 1 : 0;
                    return bNew - aNew;
                });
                break;
        }
        
        return sorted;
    }
    
    displayProducts(products) {
        if (!this.productsGrid) return;
        
        this.productsGrid.innerHTML = '';
        products.forEach(card => {
            this.productsGrid.appendChild(card.cloneNode(true));
        });
        
        this.initWishlist();
        this.initCartActions();
        
        this.toggleEmptyState(products.length === 0);
        this.hidePagination(products.length !== this.originalCards.length);
    }
    
    updateActiveFiltersDisplay() {
        if (!this.activeFiltersContainer) return;
        
        const hasActiveFilters = 
            this.activeFilters.price.min > 0 || 
            this.activeFilters.price.max < Infinity ||
            this.activeFilters.availability.length > 0 ||
            this.activeFilters.brands.length > 0 ||
            this.activeFilters.power.length > 0 ||
            this.activeFilters.waterproof.length > 0 ||
            this.activeFilters.vibration.length > 0 ||
            this.activeFilters.types.length > 0 ||
            this.currentSort !== 'default';
        
        if (!hasActiveFilters) {
            this.activeFiltersContainer.classList.add('hidden');
            return;
        }
        
        this.activeFiltersContainer.classList.remove('hidden');
        this.activeFiltersContainer.innerHTML = '';
        
        if (this.activeFilters.price.min > 0 || this.activeFilters.price.max < Infinity) {
            this.createFilterChip('price', `Ціна: ${this.activeFilters.price.min || 0} - ${this.activeFilters.price.max === Infinity ? '∞' : this.activeFilters.price.max} ₴`);
        }
        
        this.activeFilters.availability.forEach(value => {
            this.createFilterChip('availability', value === 'in_stock' ? 'В наявності' : 'Під замовлення');
        });
        
        this.activeFilters.brands.forEach(brand => {
            const shortName = brand.split(' (')[0];
            this.createFilterChip('brand', shortName);
        });
        
        this.activeFilters.power.forEach(power => {
            const powerLabels = {
                'вбудовані акумулятори': 'Акумулятор',
                'батарейки': 'Батарейки',
                'від мережі 220V': 'Мережа 220V'
            };
            this.createFilterChip('power', powerLabels[power] || power);
        });
        
        this.activeFilters.waterproof.forEach(waterproof => {
            const waterproofLabels = {
                'можна занурювати': 'Повністю водостійкий',
                'водостійка': 'Водостійкий',
                'захист від бризок': 'Захист від бризок'
            };
            this.createFilterChip('waterproof', waterproofLabels[waterproof] || waterproof);
        });
        
        this.activeFilters.vibration.forEach(vibration => {
            this.createFilterChip('vibration', vibration === 'так' ? 'З вібрацією' : 'Без вібрації');
        });
        
        this.activeFilters.types.forEach(type => {
            const typeLabels = {
                'new': 'Новинки',
                'sale': 'Акційні',
                'top': 'Хіти продажу'
            };
            this.createFilterChip('type', typeLabels[type]);
        });
    }
    
    createFilterChip(filterType, text) {
        const chip = document.createElement('div');
        chip.className = 'filter-chip';
        chip.innerHTML = `
            <span>${text}</span>
            <button type="button" class="filter-chip__remove" aria-label="Видалити фільтр">✕</button>
        `;
        
        chip.querySelector('.filter-chip__remove').addEventListener('click', () => {
            this.removeFilter(filterType, text);
        });
        
        this.activeFiltersContainer.appendChild(chip);
    }
    
    removeFilter(filterType, text) {
        switch (filterType) {
            case 'price':
                if (this.filters.priceMin) this.filters.priceMin.value = '';
                if (this.filters.priceMax) this.filters.priceMax.value = '';
                break;
            case 'availability':
                this.filters.availability.forEach(cb => {
                    if ((cb.value === 'in_stock' && text === 'В наявності') || 
                        (cb.value === 'out_of_stock' && text === 'Під замовлення')) {
                        cb.checked = false;
                    }
                });
                break;
            case 'brand':
                this.filters.brands.forEach(cb => {
                    if (cb.value.startsWith(text)) cb.checked = false;
                });
                break;
            case 'power':
            case 'waterproof':
            case 'vibration':
                this.filters[filterType].forEach(cb => cb.checked = false);
                break;
            case 'type':
                this.filters.types.forEach(cb => cb.checked = false);
                break;
        }
        
        this.applyFilters();
    }
    
    clearFilters() {
        if (this.filters.priceMin) this.filters.priceMin.value = '';
        if (this.filters.priceMax) this.filters.priceMax.value = '';
        
        const allCheckboxes = [
            ...this.filters.availability,
            ...this.filters.brands,
            ...this.filters.power,
            ...this.filters.waterproof,
            ...this.filters.vibration,
            ...this.filters.types
        ];
        
        allCheckboxes.forEach(cb => cb.checked = false);
        
        this.currentSort = 'default';
        if (this.sortSelectBtn) {
            this.sortSelectBtn.querySelector('.sort-select-text').textContent = 'Сортувати';
        }
        
        this.applyFilters();
    }
    
    updateResultsCount(filtered, total) {
        if (this.resultsCount) {
            this.resultsCount.textContent = `Показано ${filtered} з ${total} товарів`;
        }
    }
    
    showSkeleton(show) {
        if (!this.productsGrid || !this.skeletonGrid) return;
        
        if (show) {
            this.productsGrid.classList.add('hidden');
            this.skeletonGrid.classList.remove('hidden');
        } else {
            this.productsGrid.classList.remove('hidden');
            this.skeletonGrid.classList.add('hidden');
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
    
    hidePagination(hide) {
        const pagination = document.querySelector('.pagination');
        if (pagination) {
            pagination.style.display = hide ? 'none' : 'flex';
        }
    }
    
    initFiltersToggle() {
        const filtersToggle = document.getElementById('filtersToggle');
        const filtersContent = document.getElementById('filtersContent');
        
        if (filtersToggle && filtersContent) {
            filtersToggle.addEventListener('click', () => {
                filtersToggle.classList.toggle('active');
                filtersContent.classList.toggle('active');
            });
        }
    }
    
    initMobileFilters() {
        if (!this.mobileFiltersBtn || !this.mobileFiltersModal) return;
        
        const modalContent = this.mobileFiltersModal.querySelector('.modal-filters__content');
        const modalBody = this.mobileFiltersModal.querySelector('.modal-filters__body');
        const closeBtn = this.mobileFiltersModal.querySelector('.modal-filters__close');
        
        this.mobileFiltersBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.openMobileFilters();
        });
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeMobileFilters());
        }
        
        this.mobileFiltersModal.addEventListener('click', (e) => {
            if (!modalContent.contains(e.target)) {
                this.closeMobileFilters();
            }
        });
        
        const applyBtn = this.mobileFiltersModal.querySelector('.modal-filters__apply');
        if (applyBtn) {
            applyBtn.addEventListener('click', () => {
                this.syncMobileFiltersToOriginal();
                this.closeMobileFilters();
                this.applyFilters();
            });
        }
        
        const clearBtn = this.mobileFiltersModal.querySelector('.modal-filters__clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }
    }
    
    openMobileFilters() {
        if (!this.mobileFiltersModal) return;
        
        const filtersContent = document.querySelector('.filters-content');
        const modalBody = this.mobileFiltersModal.querySelector('.modal-filters__body');
        
        if (filtersContent && modalBody) {
            const contentClone = filtersContent.cloneNode(true);
            const actionsGroup = contentClone.querySelector('.filter-group--actions');
            if (actionsGroup) {
                actionsGroup.remove();
            }
            modalBody.innerHTML = contentClone.querySelector('.filters-grid').innerHTML;
            
            const allInputs = modalBody.querySelectorAll('input[type="checkbox"], input[type="number"]');
            allInputs.forEach(input => {
                let original;
                if (input.id) {
                    original = document.getElementById(input.id);
                } else if (input.name && input.value) {
                    const selector = `.filters-content input[name="${input.name}"][value="${input.value.replace(/"/g, '\\"')}"]`;
                    original = document.querySelector(selector);
                }
                
                if (original) {
                    if (input.type === 'checkbox') {
                        input.checked = original.checked;
                    } else {
                        input.value = original.value;
                    }
                }
            });
        }
        
        this.mobileFiltersModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    isInMobileModal(element) {
        return element.closest('.mobile-filters-modal') !== null;
    }
    
    syncMobileFiltersToOriginal() {
        if (!this.mobileFiltersModal) return;
        
        const modalBody = this.mobileFiltersModal.querySelector('.modal-filters__body');
        const allInputs = modalBody.querySelectorAll('input[type="checkbox"], input[type="number"]');
        
        allInputs.forEach(input => {
            let original;
            if (input.id) {
                original = document.getElementById(input.id);
            } else if (input.name && input.type === 'checkbox' && input.value) {
                const selector = `.filters-content input[name="${input.name}"][value="${input.value.replace(/"/g, '\\"')}"]`;
                original = document.querySelector(selector);
            }
            
            if (original) {
                if (input.type === 'checkbox') {
                    original.checked = input.checked;
                } else {
                    original.value = input.value;
                }
            }
        });
    }
    
    closeMobileFilters() {
        if (!this.mobileFiltersModal) return;
        
        this.mobileFiltersModal.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    initWishlist() {
        const wishlistButtons = document.querySelectorAll('.product-card__wishlist');
        
        wishlistButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                const productId = button.dataset.productId;
                
                try {
                    const response = await fetch('/wishlist/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken()
                        },
                        body: JSON.stringify({ product_id: productId })
            });
            
            const data = await response.json();
            
                    if (data.added) {
                        button.classList.add('active');
                        this.showToast('Додано до обраного');
                } else {
                        button.classList.remove('active');
                        this.showToast('Видалено з обраного');
                    }
                } catch (error) {
                    console.error('Помилка:', error);
                    this.showToast('Помилка при додаванні до обраного', 'error');
                }
            });
        });
    }
    
    initCartActions() {
        const addToCartButtons = document.querySelectorAll('.product-card__add-cart');
        
        addToCartButtons.forEach(button => {
            if (button.disabled) return;
            
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                const productId = button.dataset.productId;
                
                try {
            const response = await fetch('/cart/add/', {
                method: 'POST',
                headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken()
                },
                        body: JSON.stringify({ product_id: productId, quantity: 1 })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast('Товар додано до кошика');
                        this.updateCartBadge(data.cart_count);
                    } else {
                        this.showToast(data.message || 'Помилка при додаванні до кошика', 'error');
            }
        } catch (error) {
                    console.error('Помилка:', error);
                    this.showToast('Помилка при додаванні до кошика', 'error');
                }
            });
        });
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    updateCartBadge(count) {
        const badges = document.querySelectorAll('.cart-badge, .mobile-cart-badge');
        badges.forEach(badge => {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        });
    }
    
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
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('productsGrid')) {
        new CatalogManager();
    }
});
