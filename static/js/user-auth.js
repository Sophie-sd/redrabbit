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
        
        const eyeIcon = toggle.querySelector('.eye-icon');
        const eyeOffIcon = toggle.querySelector('.eye-off-icon');
        
        // Initial state
        if (eyeOffIcon) {
            eyeOffIcon.style.display = 'none';
        }
        
        toggle.addEventListener('click', function() {
            const currentType = passwordInput.getAttribute('type');
            const newType = currentType === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', newType);
            
            if (eyeIcon && eyeOffIcon) {
                if (newType === 'text') {
                    eyeIcon.style.display = 'none';
                    eyeOffIcon.style.display = 'block';
                    toggle.setAttribute('aria-label', 'Приховати пароль');
                } else {
                    eyeIcon.style.display = 'block';
                    eyeOffIcon.style.display = 'none';
                    toggle.setAttribute('aria-label', 'Показати пароль');
                }
            } else {
                toggle.classList.toggle('active');
                const label = newType === 'text' ? 'Приховати пароль' : 'Показати пароль';
                toggle.setAttribute('aria-label', label);
            }
        });
    });
}

