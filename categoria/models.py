from django.db import models

class Categoria(models.Model):
    """Modelo para Categorías"""
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
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Subcategoria(models.Model):
    """Modelo para Subcategorías"""
    categoria = models.ForeignKey(
        'categoria.Categoria',
        on_delete=models.CASCADE,
        related_name='subcategorias',
        verbose_name='Categoría'
    )
    
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
        verbose_name = 'Subcategoría'
        verbose_name_plural = 'Subcategorías'
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.nombre}"
