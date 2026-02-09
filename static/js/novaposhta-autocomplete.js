class NovaPoshtaAutocomplete {
    constructor() {
        this.cityInput = document.querySelector('[data-type="city"]');
        this.warehouseInput = document.querySelector('[data-type="warehouse"]');
        this.cityRefInput = document.querySelector('input[name="nova_poshta_city_ref"]');
        this.warehouseRefInput = document.querySelector('input[name="nova_poshta_warehouse_ref"]');
        this.cityRef = null;
        this.debounceTimer = null;
        
        if (this.cityInput) {
            this.init();
        }
    }
    
    init() {
        this.createDropdowns();
        this.attachEvents();
    }
    
    createDropdowns() {
        // Dropdown для міста
        this.cityDropdown = this.createDropdownElement();
        this.cityInput.parentElement.style.position = 'relative';
        this.cityInput.parentElement.appendChild(this.cityDropdown);
        
        // Dropdown для відділення
        if (this.warehouseInput) {
            this.warehouseDropdown = this.createDropdownElement();
            this.warehouseInput.parentElement.style.position = 'relative';
            this.warehouseInput.parentElement.appendChild(this.warehouseDropdown);
        }
    }
    
    createDropdownElement() {
        const dropdown = document.createElement('div');
        dropdown.className = 'np-autocomplete-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        return dropdown;
    }
    
    attachEvents() {
        // Пошук міст
        this.cityInput.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                this.hideDropdown(this.cityDropdown);
                return;
            }
            
            this.debounceTimer = setTimeout(() => {
                this.searchCities(query);
            }, 300);
        });
        
        // Закриття при кліку поза dropdown
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.np-autocomplete')) {
                this.hideDropdown(this.cityDropdown);
                this.hideDropdown(this.warehouseDropdown);
            }
        });
        
        // Пошук відділень
        if (this.warehouseInput) {
            this.warehouseInput.addEventListener('focus', () => {
                if (this.cityRef) {
                    this.loadWarehouses(this.cityRef);
                }
            });
        }
    }
    
    async searchCities(query) {
        try {
            const response = await fetch(`/orders/api/np/cities/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success && data.data.length > 0) {
                this.showCitiesDropdown(data.data);
            } else {
                this.hideDropdown(this.cityDropdown);
            }
        } catch (error) {
            console.error('Nova Poshta cities error:', error);
        }
    }
    
    showCitiesDropdown(cities) {
        this.cityDropdown.innerHTML = '';
        
        cities.forEach(city => {
            const item = document.createElement('div');
            item.className = 'np-dropdown-item';
            item.textContent = city.label;
            item.style.cssText = `
                padding: 10px 15px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
            `;
            
            item.addEventListener('mouseenter', () => {
                item.style.backgroundColor = '#f5f5f5';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.backgroundColor = 'white';
            });
            
            item.addEventListener('click', () => {
                this.selectCity(city);
            });
            
            this.cityDropdown.appendChild(item);
        });
        
        this.cityDropdown.style.display = 'block';
    }
    
    selectCity(city) {
        this.cityInput.value = city.label;
        this.cityRef = city.ref;
        
        // Зберігаємо REF у hidden input
        if (this.cityRefInput) {
            this.cityRefInput.value = city.ref;
        }
        
        this.hideDropdown(this.cityDropdown);
        
        // Активувати поле відділення
        if (this.warehouseInput) {
            this.warehouseInput.disabled = false;
            this.warehouseInput.placeholder = 'Почніть вводити номер відділення...';
            this.warehouseInput.value = '';
            // Очищуємо REF відділення при зміні міста
            if (this.warehouseRefInput) {
                this.warehouseRefInput.value = '';
            }
            this.loadWarehouses(city.ref);
        }
    }
    
    async loadWarehouses(cityRef) {
        try {
            const response = await fetch(`/orders/api/np/warehouses/?city_ref=${encodeURIComponent(cityRef)}`);
            const data = await response.json();
            
            if (data.success && data.data.length > 0) {
                this.showWarehousesDropdown(data.data);
            }
        } catch (error) {
            console.error('Nova Poshta warehouses error:', error);
        }
    }
    
    showWarehousesDropdown(warehouses) {
        this.warehouseDropdown.innerHTML = '';
        
        warehouses.forEach(wh => {
            const item = document.createElement('div');
            item.className = 'np-dropdown-item';
            item.textContent = wh.label;
            item.style.cssText = `
                padding: 10px 15px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
            `;
            
            item.addEventListener('mouseenter', () => {
                item.style.backgroundColor = '#f5f5f5';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.backgroundColor = 'white';
            });
            
            item.addEventListener('click', () => {
                this.selectWarehouse(wh);
            });
            
            this.warehouseDropdown.appendChild(item);
        });
        
        this.warehouseDropdown.style.display = 'block';
    }
    
    selectWarehouse(warehouse) {
        this.warehouseInput.value = warehouse.label;
        
        // Зберігаємо REF у hidden input
        if (this.warehouseRefInput) {
            this.warehouseRefInput.value = warehouse.ref;
        }
        
        this.hideDropdown(this.warehouseDropdown);
    }
    
    hideDropdown(dropdown) {
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }
}

// Ініціалізація при завантаженні
document.addEventListener('DOMContentLoaded', () => {
    new NovaPoshtaAutocomplete();
});
