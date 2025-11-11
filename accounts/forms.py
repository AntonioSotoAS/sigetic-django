from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserForm(forms.ModelForm):
    """Formulario para crear/editar usuarios"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        label='Contraseña',
        required=False
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        label='Confirmar Contraseña',
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'dni',
            'nombres', 'apellidos_paterno', 'apellidos_materno',
            'correo', 'telefono', 'rol', 'sede', 'cargo', 'dependencia',
            'sedes_soporte', 'activo', 'is_staff', 'is_active'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DNI'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres'
            }),
            'apellidos_paterno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido Paterno'
            }),
            'apellidos_materno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido Materno'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'rol': forms.Select(attrs={
                'class': 'form-control'
            }),
            'sede': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cargo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'dependencia': forms.Select(attrs={
                'class': 'form-control'
            }),
            'sedes_soporte': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'multiple': True,
                'size': 5
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'username': 'Usuario *',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Email *',
            'dni': 'DNI',
            'nombres': 'Nombres',
            'apellidos_paterno': 'Apellido Paterno',
            'apellidos_materno': 'Apellido Materno',
            'correo': 'Correo',
            'telefono': 'Teléfono',
            'rol': 'Rol *',
            'sede': 'Sede',
            'cargo': 'Cargo',
            'dependencia': 'Dependencia',
            'sedes_soporte': 'Sedes de Soporte',
            'activo': 'Activo',
            'is_staff': 'Es Staff',
            'is_active': 'Es Activo',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class UserCreateForm(UserForm):
    """Formulario específico para crear usuarios"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        label='Contraseña *',
        required=True
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        label='Confirmar Contraseña *',
        required=True
    )

class ProfileForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña (dejar vacío para no cambiar)'
        }),
        label='Nueva Contraseña',
        required=False,
        help_text='Deja este campo vacío si no deseas cambiar tu contraseña'
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        label='Confirmar Nueva Contraseña',
        required=False
    )
    
    class Meta:
        model = User
        fields = ['foto_perfil', 'sede', 'cargo']
        widgets = {
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'sede': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cargo': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'foto_perfil': 'Foto de Perfil',
            'sede': 'Sede',
            'cargo': 'Cargo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo sedes activas
        from sede.models import Sede
        from cargo.models import Cargo
        self.fields['sede'].queryset = Sede.objects.filter(activa=True)
        self.fields['cargo'].queryset = Cargo.objects.filter(activo=True)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            if len(password) < 8:
                raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
