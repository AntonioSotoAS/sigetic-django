from django.db import models
from django.core.validators import RegexValidator


class BaseModel(models.Model):
    """
    Modelo abstracto base con campos comunes para personas.
    Incluye: nombres, apellidos, DNI y teléfono.
    """
    # Validadores
    dni_validator = RegexValidator(
        regex=r'^\d{8}$',
        message='El DNI debe tener exactamente 8 dígitos numéricos.'
    )
    
    telefono_validator = RegexValidator(
        regex=r'^\d{9}$',
        message='El teléfono debe tener exactamente 9 dígitos numéricos.'
    )
    
    # Campos
    nombres = models.CharField(
        max_length=100,
        verbose_name='Nombres',
        help_text='Ingrese los nombres de la persona'
    )
    
    apellido_paterno = models.CharField(
        max_length=100,
        verbose_name='Apellido Paterno',
        help_text='Ingrese el apellido paterno'
    )
    
    apellido_materno = models.CharField(
        max_length=100,
        verbose_name='Apellido Materno',
        help_text='Ingrese el apellido materno',
        blank=True,
        null=True
    )
    
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[dni_validator],
        verbose_name='DNI',
        help_text='Ingrese el DNI (8 dígitos)'
    )
    
    telefono = models.CharField(
        max_length=9,
        validators=[telefono_validator],
        verbose_name='Teléfono',
        help_text='Ingrese el teléfono (9 dígitos)',
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        abstract = True
        ordering = ['apellido_paterno', 'apellido_materno', 'nombres']
    
    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno or ''}".strip()
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo de la persona"""
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno or ''}".strip()
