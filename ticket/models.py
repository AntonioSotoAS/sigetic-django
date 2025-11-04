from django.db import models
from django.contrib.auth import get_user_model
from categoria.models import Categoria, Subcategoria
from dependencia.models import Dependencia
from sede.models import Sede

User = get_user_model()

class Ticket(models.Model):
    """Modelo para tickets/solicitudes IT"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    titulo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Título'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name='Prioridad'
    )
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        related_name='tickets',
        verbose_name='Categoría',
        blank=True,
        null=True
    )
    
    subcategoria = models.ForeignKey(
        Subcategoria,
        on_delete=models.SET_NULL,
        related_name='tickets',
        verbose_name='Subcategoría',
        blank=True,
        null=True
    )
    
    dependencia = models.ForeignKey(
        Dependencia,
        on_delete=models.SET_NULL,
        related_name='tickets',
        verbose_name='Dependencia',
        blank=True,
        null=True
    )
    
    sede = models.ForeignKey(
        Sede,
        on_delete=models.SET_NULL,
        related_name='tickets',
        verbose_name='Sede',
        blank=True,
        null=True
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='Usuario',
        blank=True,
        null=True
    )
    
    tecnico = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='tickets_asignados',
        verbose_name='Técnico',
        blank=True,
        null=True
    )
    
    fecha_asignacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Asignación'
    )
    
    fecha_resolucion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Resolución'
    )
    
    fecha_cierre = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Cierre'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Eliminación'
    )
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo or 'Sin título'} - {self.user.username if self.user else 'Sin usuario'}"
