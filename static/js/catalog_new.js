class CatalogManager {
    constructor() {
        this.productsGrid = document.getElementById('productsGrid');
        this.skeletonGrid = document.getElementById('skeletonGrid');
        this.productCards = [];
        this.originalCards = [];
        this.activeFilters = {
            price: { min: 0, max: Infinity },
            subcategories: []
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
            subcategories: document.querySelectorAll('input[name="subcategory"]')
        };
        
        this.clearFiltersBtn = document.getElementById('clearAllFilters');
        this.applyFiltersBtn = document.getElementById('applyFiltersBtn');
        this.activeFiltersContainer = document.getElementById('activeFilters');
        this.mobileFiltersBtn = document.getElementById('mobileFiltersBtn');
        this.mobileFiltersModal = document.getElementById('mobileFiltersModal');
        this.sortSelectBtn = document.getElementById('sortSelectBtn');
        this.sortDropdown = document.getElementById('sortDropdown');
        
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
        
        this.filters.subcategories.forEach(checkbox => {
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
        
        const desktopSortBtn = document.getElementById('desktopSortBtn');
        const desktopSortDropdown = document.getElementById('desktopSortDropdown');
        
        if (desktopSortBtn && desktopSortDropdown) {
            desktopSortBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                desktopSortDropdown.classList.toggle('hidden');
                desktopSortBtn.classList.toggle('active');
            });
            
            desktopSortDropdown.querySelectorAll('.sort-option').forEach(option => {
                option.addEventListener('click', () => {
                    const value = option.dataset.value;
                    this.currentSort = value;
                    desktopSortBtn.querySelector('.sort-text').textContent = option.textContent;
                    desktopSortDropdown.classList.add('hidden');
                    desktopSortBtn.classList.remove('active');
                    this.applyFilters();
                });
            });
            
            document.addEventListener('click', (e) => {
                if (!desktopSortBtn.contains(e.target) && !desktopSortDropdown.contains(e.target)) {
                    desktopSortDropdown.classList.add('hidden');
                    desktopSortBtn.classList.remove('active');
                }
            });
        }
    }
    
    loadInitialData() {
        this.productCards = Array.from(document.querySelectorAll('.product-card'));
        this.originalCards = [...this.productCards];
    }
    
    applyFilters() {
        this.showSkeleton(true);
        
        this.collectActiveFilters();
        const filteredCards = this.filterProducts();
        const sortedCards = this.sortProducts(filteredCards);
        
        setTimeout(() => {
            this.displayProducts(sortedCards);
            this.updateActiveFiltersDisplay();
            this.showSkeleton(false);
        }, 300);
    }
    
    collectActiveFilters() {
        const priceMin = parseFloat(this.filters.priceMin?.value) || 0;
        const priceMax = parseFloat(this.filters.priceMax?.value) || Infinity;
        this.activeFilters.price = { min: priceMin, max: priceMax };
        
        this.activeFilters.subcategories = Array.from(this.filters.subcategories)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
    }
    
    filterProducts() {
        return this.originalCards.filter(card => {
            const price = parseFloat(card.dataset.salePrice);
            if (price < this.activeFilters.price.min || price > this.activeFilters.price.max) {
                return false;
            }
            
            if (this.activeFilters.subcategories.length > 0) {
                const categories = (card.dataset.categories || '').split(',');
                const hasMatch = this.activeFilters.subcategories.some(slug => 
                    categories.includes(slug)
                );
                if (!hasMatch) return false;
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
            this.activeFilters.subcategories.length > 0;
        
        if (!hasActiveFilters) {
            this.activeFiltersContainer.classList.add('hidden');
            return;
        }
        
        this.activeFiltersContainer.classList.remove('hidden');
        this.activeFiltersContainer.innerHTML = '';
        
        if (this.activeFilters.price.min > 0 || this.activeFilters.price.max < Infinity) {
            this.createFilterChip('price', `Ціна: ${this.activeFilters.price.min || 0} - ${this.activeFilters.price.max === Infinity ? '∞' : this.activeFilters.price.max} ₴`);
        }
        
        this.activeFilters.subcategories.forEach(slug => {
            const checkbox = Array.from(this.filters.subcategories).find(cb => cb.value === slug);
            if (checkbox) {
                const label = checkbox.closest('label').querySelector('span').textContent;
                this.createFilterChip('subcategory', label);
            }
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
        if (filterType === 'price') {
            if (this.filters.priceMin) this.filters.priceMin.value = '';
            if (this.filters.priceMax) this.filters.priceMax.value = '';
        } else if (filterType === 'subcategory') {
            this.filters.subcategories.forEach(cb => {
                const label = cb.closest('label').querySelector('span').textContent;
                if (label === text) cb.checked = false;
            });
        }
        
        this.applyFilters();
    }
    
    clearFilters() {
        if (this.filters.priceMin) this.filters.priceMin.value = '';
        if (this.filters.priceMax) this.filters.priceMax.value = '';
        
        this.filters.subcategories.forEach(cb => cb.checked = false);
        
        this.currentSort = 'default';
        if (this.sortSelectBtn) {
            this.sortSelectBtn.querySelector('.sort-select-text').textContent = 'Сортувати';
        }
        
        this.applyFilters();
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
                    const response = await fetch(`/cart/add/${productId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken()
                        },
                        body: JSON.stringify({ quantity: 1 })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.showToast('Товар додано до кошика');
                        document.dispatchEvent(new CustomEvent('cart:updated', { 
                            detail: { count: data.cart_count } 
                        }));
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
        if (window.Toast) {
            window.Toast.show(message, type);
        }
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

