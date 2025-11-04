from django.contrib import admin
from .models import Categoria, Subcategoria


class SubcategoriaInline(admin.TabularInline):
    """Inline para mostrar subcategorías dentro de categorías"""
    model = Subcategoria
    extra = 1
    fields = ('nombre', 'activo')


class CategoriaAdmin(admin.ModelAdmin):
    """Admin para Categoría - Solo superadmin puede crear"""
    list_display = ('nombre', 'activo', 'created_at')
    search_fields = ('nombre',)
    list_filter = ('activo', 'created_at')
    ordering = ('nombre',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SubcategoriaInline]
    
    fieldsets = (
        ('Información de la Categoría', {
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


class SubcategoriaAdmin(admin.ModelAdmin):
    """Admin para Subcategoría - Solo superadmin puede crear"""
    list_display = ('nombre', 'categoria', 'activo', 'created_at')
    search_fields = ('nombre', 'categoria__nombre')
    list_filter = ('activo', 'categoria', 'created_at')
    ordering = ('categoria', 'nombre')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información de la Subcategoría', {
            'fields': ('categoria', 'nombre', 'activo')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Solo superadmin puede agregar"""
        return request.user.is_superuser


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Subcategoria, SubcategoriaAdmin)
