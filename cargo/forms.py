from django import forms
from .models import Cargo

class CargoForm(forms.ModelForm):
    """Formulario para crear/editar Cargos"""
    
    class Meta:
        model = Cargo
        fields = ['nombre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cargo'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre': 'Nombre *',
            'activo': 'Activo',
        }
