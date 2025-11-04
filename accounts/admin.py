from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TelegramGrupoSede

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin para usuarios personalizados"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'activo', 'is_staff', 'date_joined')
    list_filter = ('rol', 'activo', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'dni', 'nombres')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('username', 'password', 'first_name', 'last_name', 'email')
        }),
        ('Información Personal', {
            'fields': ('dni', 'nombres', 'apellidos_paterno', 'apellidos_materno', 'correo', 'telefono', 'foto_perfil')
        }),
        ('Información Laboral', {
            'fields': ('rol', 'sede', 'cargo', 'dependencia', 'sedes_soporte')
        }),
        ('Telegram Bot', {
            'fields': ('bot_vinculado', 'telegram_chat_id')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'activo', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'password_resetada')
        }),
    )
    
    add_fieldsets = (
        ('Información Básica', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name')
        }),
        ('Información Personal', {
            'fields': ('dni', 'nombres', 'apellidos_paterno', 'apellidos_materno', 'correo', 'telefono')
        }),
        ('Información Laboral', {
            'fields': ('rol', 'sede', 'cargo', 'dependencia', 'sedes_soporte')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'activo')
        }),
    )
    
    def has_add_permission(self, request):
        """Solo superadmin puede agregar"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Solo superadmin puede modificar"""
        return request.user.is_superuser


@admin.register(TelegramGrupoSede)
class TelegramGrupoSedeAdmin(admin.ModelAdmin):
    """Admin para grupos de Telegram por sede"""
    
    list_display = ('sede', 'grupo_chat_id', 'nombre_grupo', 'activo', 'created_at')
    list_filter = ('activo', 'created_at')
    search_fields = ('sede__nombre', 'grupo_chat_id', 'nombre_grupo')
    ordering = ('sede__nombre',)
    
    fieldsets = (
        ('Información del Grupo', {
            'fields': ('sede', 'grupo_chat_id', 'nombre_grupo', 'activo')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        """Solo superadmin puede agregar"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Solo superadmin puede modificar"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Solo superadmin puede eliminar"""
        return request.user.is_superuser