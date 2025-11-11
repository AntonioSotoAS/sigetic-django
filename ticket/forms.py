from django import forms
from .models import Ticket
from categoria.models import Categoria, Subcategoria
from sede.models import Sede
from dependencia.models import Dependencia

class TicketForm(forms.ModelForm):
    """Formulario para crear tickets"""
    
    sede = forms.ModelChoiceField(
        queryset=Sede.objects.filter(activa=True),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_sede'
        }),
        label='Sede / Ubicación',
        required=False,
        empty_label='Seleccione una sede'
    )
    
    dependencia = forms.ModelChoiceField(
        queryset=Dependencia.objects.filter(activo=True),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_dependencia'
        }),
        label='Dependencia / Departamento',
        required=False,
        empty_label='Seleccione una dependencia'
    )
    
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activo=True),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_categoria'
        }),
        label='Categoría *',
        required=True,
        empty_label='Seleccione una categoría'
    )
    
    subcategoria = forms.ModelChoiceField(
        queryset=Subcategoria.objects.none(),  # Se actualizará dinámicamente
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_subcategoria'
        }),
        label='Subcategoría',
        required=False,
        empty_label='Seleccione una subcategoría'
    )
    
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe tu problema en detalle...',
            'id': 'descripcion'
        }),
        label='Descripción detallada *',
        required=True
    )
    
    prioridad = forms.ChoiceField(
        choices=Ticket.PRIORIDAD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_prioridad'
        }),
        label='Prioridad',
        required=False,
        initial='media'
    )
    
    class Meta:
        model = Ticket
        fields = ['sede', 'dependencia', 'categoria', 'subcategoria', 'descripcion', 'prioridad']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Preseleccionar sede y dependencia del usuario si están disponibles
        if user and user.sede:
            self.fields['sede'].initial = user.sede
        if user and user.dependencia:
            self.fields['dependencia'].initial = user.dependencia
        
        # Filtrar dependencias por sede si hay una sede seleccionada
        if 'sede' in self.data and self.data['sede']:
            try:
                sede_id = int(self.data.get('sede'))
                self.fields['dependencia'].queryset = Dependencia.objects.filter(
                    sede_id=sede_id, activo=True
                ).order_by('nombre')
            except (ValueError, TypeError):
                pass
        
        # Filtrar subcategorías por categoría si hay una categoría seleccionada
        if 'categoria' in self.data and self.data['categoria']:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = Subcategoria.objects.filter(
                    categoria_id=categoria_id, activo=True
                ).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.categoria:
            self.fields['subcategoria'].queryset = Subcategoria.objects.filter(
                categoria=self.instance.categoria, activo=True
            ).order_by('nombre')
