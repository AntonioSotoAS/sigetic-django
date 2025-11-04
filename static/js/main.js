// JavaScript global del proyecto SIGETIC

document.addEventListener('DOMContentLoaded', function() {
    console.log('SIGETIC - Sistema cargado correctamente');
    
    // Aquí puedes agregar funciones globales que se usarán en todo el proyecto
});

// Función para mostrar/ocultar contraseña
function togglePasswordVisibility(inputId, buttonId) {
    const passwordInput = document.getElementById(inputId);
    const toggleButton = document.getElementById(buttonId);
    
    if (passwordInput && toggleButton) {
        toggleButton.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Cambiar el ícono
            const icon = toggleButton.querySelector('span');
            if (icon) {
                icon.textContent = type === 'password' ? '👁️' : '🙈';
            }
        });
    }
}

// Función para validar formularios
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', function(e) {
            // Aquí puedes agregar validaciones personalizadas
            return true;
        });
    }
}

