from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class LoginForm(AuthenticationForm):
    """Formulario de login con username y password"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu usuario',
            'autofocus': True,
            'id': 'username-input'
        }),
        label='Usuario'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña',
            'id': 'password-input'
        }),
        label='Contraseña'
    )

    class Meta:
        fields = ['username', 'password']
    
    def confirm_login_allowed(self, user):
        """
        Verifica que el usuario puede iniciar sesión.
        Además de is_active, también verifica el campo activo personalizado.
        """
        super().confirm_login_allowed(user)
        
        # Verificar también el campo activo personalizado
        if not user.activo:
            raise ValidationError(
                'Esta cuenta ha sido desactivada. Por favor, contacta al administrador.',
                code='inactive',
            )

