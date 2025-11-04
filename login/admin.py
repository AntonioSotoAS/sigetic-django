from django.contrib import admin
from .models import BaseModel


class BaseModelAdmin(admin.ModelAdmin):
    """
    Clase base de administrador reutilizable para modelos que hereden de BaseModel.
    Incluye configuración común para los campos: nombres, apellidos, DNI y teléfono.
    """
    # Campos a mostrar en la lista
    list_display = ('dni', 'nombres', 'apellido_paterno', 'apellido_materno', 'telefono', 'created_at')
    
    # Campos por los que se puede buscar
    search_fields = ('dni', 'nombres', 'apellido_paterno', 'apellido_materno', 'telefono')
    
    # Filtros laterales
    list_filter = ('created_at', 'updated_at')
    
    # Ordenamiento por defecto
    ordering = ('apellido_paterno', 'apellido_materno', 'nombres')
    
    # Campos de solo lectura (para timestamps)
    readonly_fields = ('created_at', 'updated_at')
    
    # Agrupar campos en secciones
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellido_paterno', 'apellido_materno', 'dni', 'telefono')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Sección colapsable
        }),
    )
    
    # Configuración para campos relacionados
    autocomplete_fields = []
    
    # Campos que aparecen en la vista de lista con links
    list_display_links = ('dni', 'nombres')


# Nota: Como BaseModel es abstracto, no se puede registrar directamente.
# Este admin se usa cuando otros modelos hereden de BaseModel, por ejemplo:
# 
# from django.contrib import admin
# from .models import MiModelo
# from login.admin import BaseModelAdmin
#
# @admin.register(MiModelo)
# class MiModeloAdmin(BaseModelAdmin):
#     pass
#
# O simplemente:
# admin.site.register(MiModelo, BaseModelAdmin)
