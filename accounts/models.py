from django.contrib.auth.models import AbstractUser
from django.db import models
from sede.models import Sede
from cargo.models import Cargo
from dependencia.models import Dependencia
import os

def user_profile_photo_path(instance, filename):
    """Genera la ruta de subida para las fotos de perfil: media/fotoperfil/username/filename"""
    # Obtener el username del usuario
    username = None
    
    # Intentar obtener el username de diferentes formas
    if instance and hasattr(instance, 'username'):
        if instance.username:
            username = instance.username
        # Si el usuario no tiene username pero tiene ID, obtenerlo de la BD
        elif instance.id:
            try:
                # Usar get_user_model para evitar importación circular
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_obj = User.objects.get(id=instance.id)
                username = user_obj.username
            except:
                pass
    
    # Si aún no tenemos username, usar 'sin_usuario'
    if not username:
        username = 'sin_usuario'
    
    # Limpiar el username para que sea seguro para usar en rutas de archivos
    # Reemplazar caracteres no permitidos
    import re
    username = re.sub(r'[^\w\-_\.]', '_', username)
    
    # Retornar la ruta: media/fotoperfil/username/filename
    path = f'fotoperfil/{username}/{filename}'
    return path

class User(AbstractUser):
    """Modelo de usuario personalizado con campos adicionales"""
    
    ROL_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('jefe_soporte', 'Jefe de Soporte'),
        ('ingeniero_soporte', 'Ingeniero de Soporte'),
        ('usuario', 'Usuario'),
    ]
    
    # Campos adicionales
    dni = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        verbose_name='DNI'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    apellidos_materno = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Apellido Materno'
    )
    
    apellidos_paterno = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Apellido Paterno'
    )
    
    nombres = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nombres'
    )
    
    correo = models.EmailField(
        max_length=254,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Correo'
    )
    
    telefono = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    
    foto_perfil = models.ImageField(
        upload_to=user_profile_photo_path,
        blank=True,
        null=True,
        verbose_name='Foto de Perfil'
    )
    
    password_resetada = models.BooleanField(
        default=False,
        verbose_name='Password Resetada'
    )
    
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='usuario',
        verbose_name='Rol'
    )
    
    sedes_soporte = models.ManyToManyField(
        Sede,
        related_name='usuarios_soporte',
        blank=True,
        verbose_name='Sedes de Soporte',
        help_text='Selecciona las sedes que este usuario puede soportar'
    )
    
    sede = models.ForeignKey(
        Sede,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Sede'
    )
    
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Cargo'
    )
    
    dependencia = models.ForeignKey(
        Dependencia,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Dependencia'
    )
    
    # Campos de Telegram Bot
    bot_vinculado = models.BooleanField(
        default=False,
        verbose_name='Bot Vinculado',
        help_text='Indica si el usuario tiene el bot de Telegram vinculado'
    )
    
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Chat ID de Telegram',
        help_text='ID del chat de Telegram del usuario'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.username
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.nombres and self.apellidos_paterno:
            return f"{self.nombres} {self.apellidos_paterno}"
        return self.username


class TelegramGrupoSede(models.Model):
    """Modelo para grupos de Telegram por sede"""
    sede = models.OneToOneField(
        Sede,
        on_delete=models.CASCADE,
        related_name='telegram_grupo',
        verbose_name='Sede'
    )
    
    grupo_chat_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Chat ID del Grupo',
        help_text='ID del grupo de Telegram para esta sede'
    )
    
    nombre_grupo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nombre del Grupo',
        help_text='Nombre del grupo en Telegram'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el grupo está activo'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        verbose_name = 'Grupo de Telegram por Sede'
        verbose_name_plural = 'Grupos de Telegram por Sede'
        ordering = ['sede__nombre']
    
    def __str__(self):
        return f"{self.sede.nombre} - {self.grupo_chat_id}"