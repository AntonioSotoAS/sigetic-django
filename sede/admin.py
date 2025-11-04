from django.contrib import admin
from .models import Sede


class SedeAdmin(admin.ModelAdmin):
    """Admin para Sede - Solo superadmin puede crear"""
    list_display = ('nombre', 'direccion', 'telefono', 'email', 'activa', 'created_at')
    search_fields = ('nombre', 'direccion', 'email')
    list_filter = ('activa', 'created_at')
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información de la Sede', {
            'fields': ('nombre', 'direccion', 'telefono', 'email', 'activa')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Solo superadmin puede agregar"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Solo superadmin puede modificar"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Solo superadmin puede eliminar"""
        return request.user.is_superuser


admin.site.register(Sede, SedeAdmin)
