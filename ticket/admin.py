from django.contrib import admin
from .models import Ticket


class TicketAdmin(admin.ModelAdmin):
    """Admin para Ticket"""
    list_display = ('titulo', 'user', 'categoria', 'estado', 'prioridad', 'created_at')
    search_fields = ('titulo', 'descripcion', 'user__username', 'user__email')
    list_filter = ('estado', 'prioridad', 'categoria', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('titulo', 'descripcion', 'categoria', 'subcategoria', 'user')
        }),
        ('Asignación', {
            'fields': ('estado', 'prioridad', 'dependencia', 'sede', 'tecnico', 'fecha_asignacion')
        }),
        ('Fechas', {
            'fields': ('fecha_resolucion', 'fecha_cierre')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Todos pueden agregar tickets"""
        return True


admin.site.register(Ticket, TicketAdmin)
