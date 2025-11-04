from django.db import models
from sede.models import Sede

class Dependencia(models.Model):
    """Modelo para Dependencias"""
    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name='dependencias',
        verbose_name='Sede',
        blank=True,
        null=True
    )
    
    nombre = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Nombre'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
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
        verbose_name = 'Dependencia'
        verbose_name_plural = 'Dependencias'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
