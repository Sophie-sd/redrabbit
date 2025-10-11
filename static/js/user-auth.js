/**
 * User Authentication JS - password toggle functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggles();
});

function initPasswordToggles() {
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        const targetId = toggle.getAttribute('data-target');
        const passwordInput = targetId ? 
            document.getElementById(targetId) : 
            toggle.closest('.password-input-wrapper')?.querySelector('.password-field');
        
        if (!passwordInput) return;
        
        toggle.addEventListener('click', function() {
            const currentType = passwordInput.getAttribute('type');
            const newType = currentType === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', newType);
            
            toggle.classList.toggle('active');
            const label = newType === 'text' ? 'Приховати пароль' : 'Показати пароль';
            toggle.setAttribute('aria-label', label);
        });
    });
}

