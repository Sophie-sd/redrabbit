document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('orderForm');
    const submitBtn = document.getElementById('submitBtn');
    const deliveryRadios = document.querySelectorAll('input[name="delivery_method"]');
    const novaPoshtaFields = document.getElementById('novaPoshtaFields');
    const ukrposhtaFields = document.getElementById('ukrposhtaFields');
    
    if (!deliveryRadios.length || !form) return;
    
    function toggleDeliveryFields() {
        const selectedDelivery = document.querySelector('input[name="delivery_method"]:checked');
        
        if (!selectedDelivery) {
            novaPoshtaFields?.classList.remove('active');
            ukrposhtaFields?.classList.remove('active');
            return;
        }
        
        if (selectedDelivery.value === 'nova_poshta') {
            novaPoshtaFields?.classList.add('active');
            ukrposhtaFields?.classList.remove('active');
        } else if (selectedDelivery.value === 'ukrposhta') {
            ukrposhtaFields?.classList.add('active');
            novaPoshtaFields?.classList.remove('active');
        }
    }
    
    deliveryRadios.forEach(radio => {
        radio.addEventListener('change', toggleDeliveryFields);
    });
    
    toggleDeliveryFields();
    
    form.addEventListener('submit', (e) => {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Обробка...';
        }
    });
});

