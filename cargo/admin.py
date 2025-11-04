from django.contrib import admin
from .models import Cargo


class CargoAdmin(admin.ModelAdmin):
    """Admin para Cargo - Solo superadmin puede crear"""
    list_display = ('nombre', 'activo', 'created_at')
    search_fields = ('nombre',)
    list_filter = ('activo', 'created_at')
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información del Cargo', {
            'fields': ('nombre', 'activo')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Solo superadmin puede agregar"""
        return request.user.is_superuser


admin.site.register(Cargo, CargoAdmin)
