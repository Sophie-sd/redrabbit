// Custom Admin JavaScript для Beauty Shop

document.addEventListener('DOMContentLoaded', function() {
    
    // Покращуємо UX при роботі з формами
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('input[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.value = 'Збереження...';
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.value = 'Зберегти';
                }, 3000);
            }
        });
    });
    
    // Автоматичне заповнення slug полів
    const titleField = document.querySelector('#id_title');
    const slugField = document.querySelector('#id_slug');
    
    if (titleField && slugField) {
        titleField.addEventListener('input', function() {
            if (!slugField.value) {
                let slug = this.value
                    .toLowerCase()
                    .replace(/[^a-z0-9а-я\s-]/g, '')
                    .replace(/\s+/g, '-')
                    .replace(/-+/g, '-')
                    .trim();
                
                // Транслітерація українських символів
                const ukrainianToLatin = {
                    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'ґ': 'g',
                    'д': 'd', 'е': 'e', 'є': 'ye', 'ж': 'zh', 'з': 'z',
                    'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k',
                    'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
                    'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
                    'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
                    'ю': 'yu', 'я': 'ya', 'ь': '', 'ъ': ''
                };
                
                for (let [uk, lat] of Object.entries(ukrainianToLatin)) {
                    slug = slug.replace(new RegExp(uk, 'g'), lat);
                }
                
                slugField.value = slug.substring(0, 50); // Обмежуємо довжину
            }
        });
    }
    
    // Покращуємо відображення зображень з попереднім переглядом
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Створюємо попередній перегляд
                    let preview = input.parentNode.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-preview';
                        preview.style.cssText = `
                            margin-top: 10px;
                            border: 2px dashed #ddd;
                            border-radius: 5px;
                            padding: 10px;
                            text-align: center;
                        `;
                        input.parentNode.appendChild(preview);
                    }
                    
                    preview.innerHTML = `
                        <img src="${e.target.result}" 
                             style="max-width: 200px; max-height: 200px; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">${file.name}</p>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    });
    
    // Додаємо підтвердження при видаленні
    const deleteLinks = document.querySelectorAll('a[href*="delete"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Ви впевнені, що хочете видалити цей елемент?')) {
                e.preventDefault();
            }
        });
    });
    
    // Покращуємо роботу з CKEditor
    if (typeof CKEDITOR !== 'undefined') {
        CKEDITOR.on('instanceReady', function(event) {
            const editor = event.editor;
            
            // Додаємо кастомні стилі
            editor.addContentsCss('/static/css/ckeditor-custom.css');
            
            // Автозбереження
            let autoSaveTimer;
            editor.on('change', function() {
                clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(function() {
                    console.log('Автозбереження контенту...');
                    // Тут можна додати логіку автозбереження
                }, 5000);
            });
        });
    }
    
    // Покращуємо таблиці з результатами
    const resultTable = document.querySelector('#result_list');
    if (resultTable) {
        // Додаємо зебру для рядків
        const rows = resultTable.querySelectorAll('tbody tr');
        rows.forEach((row, index) => {
            if (index % 2 === 0) {
                row.style.backgroundColor = '#f8f9fa';
            }
        });
        
        // Додаємо можливість сортування (якщо не вже є)
        const headers = resultTable.querySelectorAll('thead th');
        headers.forEach(header => {
            if (!header.querySelector('a')) return;
            
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                header.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    header.style.transform = 'scale(1)';
                }, 100);
            });
        });
    }
    
    // Покращуємо роботу з фільтрами
    const filterSidebar = document.querySelector('#changelist-filter');
    if (filterSidebar) {
        const filterLinks = filterSidebar.querySelectorAll('a');
        filterLinks.forEach(link => {
            link.addEventListener('click', function() {
                // Додаємо анімацію завантаження
                const loader = document.createElement('div');
                loader.innerHTML = '⏳ Завантаження...';
                loader.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.8); color: white; padding: 10px 20px; border-radius: 5px; z-index: 9999;';
                document.body.appendChild(loader);
                
                setTimeout(() => {
                    document.body.removeChild(loader);
                }, 1000);
            });
        });
    }
});

// Утиліти для адмінки
window.BeautyShopAdmin = {
    // Показати повідомлення
    showMessage: function(text, type = 'success') {
        const message = document.createElement('div');
        message.className = `alert alert-${type}`;
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#28a745' : '#dc3545'};
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        message.textContent = text;
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(message);
            }, 300);
        }, 3000);
    },
    
    // Копіювати текст
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showMessage('Скопійовано в буфер!');
        });
    }
};
