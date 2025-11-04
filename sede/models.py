from django.db import models

class Sede(models.Model):
    """Modelo para Sedes"""
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre'
    )
    
    direccion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    
    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Email'
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name='Activa'
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
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
