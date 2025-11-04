// JavaScript específico para el login

document.addEventListener('DOMContentLoaded', function() {
    // Toggle para mostrar/ocultar contraseña
    const togglePassword = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password-input');
    const eyeIcon = document.getElementById('eye-icon');

    if (togglePassword && passwordInput && eyeIcon) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            eyeIcon.textContent = type === 'password' ? '👁️' : '🙈';
        });
    }
    
    // Validación del formulario de login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            // Agregar validaciones adicionales si es necesario
            const username = document.getElementById('username-input');
            const password = document.getElementById('password-input');
            
            if (username && !username.value.trim()) {
                e.preventDefault();
                alert('Por favor, ingresa tu usuario');
                username.focus();
                return false;
            }
            
            if (password && !password.value) {
                e.preventDefault();
                alert('Por favor, ingresa tu contraseña');
                password.focus();
                return false;
            }
        });
    }
});

