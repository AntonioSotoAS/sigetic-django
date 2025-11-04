from django.contrib import admin
from .models import Dependencia


class DependenciaAdmin(admin.ModelAdmin):
    """Admin para Dependencia - Solo superadmin puede crear"""
    list_display = ('nombre', 'sede', 'activo', 'created_at')
    search_fields = ('nombre', 'descripcion', 'sede__nombre')
    list_filter = ('activo', 'sede', 'created_at')
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información de la Dependencia', {
            'fields': ('sede', 'nombre', 'descripcion', 'activo')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Solo superadmin puede agregar"""
        return request.user.is_superuser


admin.site.register(Dependencia, DependenciaAdmin)
