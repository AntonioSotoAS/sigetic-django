from django.db import models

class Cargo(models.Model):
    """Modelo para Cargos"""
    nombre = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Nombre'
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
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
