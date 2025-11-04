from django import forms
from .models import Categoria, Subcategoria

class CategoriaForm(forms.ModelForm):
    """Formulario para crear/editar Categorías"""
    
    class Meta:
        model = Categoria
        fields = ['nombre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre': 'Nombre *',
            'activo': 'Activo',
        }

class SubcategoriaForm(forms.ModelForm):
    """Formulario para crear/editar Subcategorías"""
    
    class Meta:
        model = Subcategoria
        fields = ['categoria', 'nombre', 'activo']
        widgets = {
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la subcategoría'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'categoria': 'Categoría *',
            'nombre': 'Nombre *',
            'activo': 'Activo',
        }

