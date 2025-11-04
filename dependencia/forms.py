from django import forms
from .models import Dependencia
from sede.models import Sede

class DependenciaForm(forms.ModelForm):
    """Formulario para crear/editar Dependencias"""
    
    class Meta:
        model = Dependencia
        fields = ['sede', 'nombre', 'descripcion', 'activo']
        widgets = {
            'sede': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la dependencia'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la dependencia',
                'rows': 3
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'sede': 'Sede',
            'nombre': 'Nombre *',
            'descripcion': 'Descripción',
            'activo': 'Activo',
        }
