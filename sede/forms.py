from django import forms
from .models import Sede

class SedeForm(forms.ModelForm):
    """Formulario para crear/editar Sedes"""
    
    class Meta:
        model = Sede
        fields = ['nombre', 'direccion', 'telefono', 'email', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la sede'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre': 'Nombre *',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'email': 'Email',
            'activa': 'Activa',
        }

