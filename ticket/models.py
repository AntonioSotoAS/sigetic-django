from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
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
    
    imagenes_urls = models.JSONField(
        default=list,
        blank=True,
        verbose_name='URLs de Imágenes',
        help_text='Lista de URLs de las imágenes adjuntas al ticket'
    )
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo or 'Sin título'} - {self.user.username if self.user else 'Sin usuario'}"
    
    def actualizar_imagenes_urls(self):
        """Actualiza el campo imagenes_urls con las URLs actuales de las imágenes"""
        urls = []
        for imagen_obj in self.imagenes.all():
            if imagen_obj.imagen:
                # Construir la URL completa de la imagen
                url = imagen_obj.imagen.url
                urls.append(url)
        self.imagenes_urls = urls
        self.save(update_fields=['imagenes_urls'])
        return urls
    
    def get_imagenes_urls(self):
        """Retorna una lista con las URLs de todas las imágenes del ticket"""
        # Si el campo está vacío o desactualizado, actualizarlo
        if not self.imagenes_urls:
            return self.actualizar_imagenes_urls()
        return self.imagenes_urls or []


def ticket_image_upload_path(instance, filename):
    """Genera la ruta de subida para las imágenes de tickets: media/tickets/idticket/imagenes/"""
    # Obtener el ID del ticket
    # Intentar obtener el ID de diferentes formas
    ticket_id = None
    
    # Primero intentar desde instance.ticket.id (si el ticket ya está guardado)
    if instance and hasattr(instance, 'ticket'):
        if instance.ticket and hasattr(instance.ticket, 'id') and instance.ticket.id:
            ticket_id = instance.ticket.id
        # Si el ticket no tiene ID pero tenemos el objeto, intentar guardarlo
        elif instance.ticket and not instance.ticket.id:
            try:
                instance.ticket.save()
                ticket_id = instance.ticket.id
            except:
                pass
    
    # Si no funcionó, intentar desde ticket_id (ForeignKey)
    if not ticket_id and hasattr(instance, 'ticket_id') and instance.ticket_id:
        ticket_id = instance.ticket_id
    
    # Si aún no tenemos ID, usar 'sin_ticket'
    if not ticket_id:
        ticket_id = 'sin_ticket'
        print(f"⚠️ No se pudo obtener el ID del ticket, usando 'sin_ticket'")
    
    # Retornar la ruta: media/tickets/idticket/imagenes/filename
    path = f'tickets/{ticket_id}/imagenes/{filename}'
    print(f"📁 Ruta de imagen generada: {path} (ticket_id: {ticket_id})")
    return path


class TicketImage(models.Model):
    """Modelo para almacenar imágenes adjuntas a los tickets"""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name='Ticket'
    )
    
    imagen = models.ImageField(
        upload_to=ticket_image_upload_path,
        verbose_name='Imagen'
    )
    
    def save(self, *args, **kwargs):
        # Asegurar que el ticket tenga un ID antes de guardar
        # Esto es crítico porque upload_to necesita el ticket.id
        if self.ticket:
            if not self.ticket.id:
                print(f"   🔄 Guardando ticket primero para obtener ID...")
                self.ticket.save()
                print(f"   ✅ Ticket guardado con ID: {self.ticket.id}")
            else:
                print(f"   ✅ Ticket ya tiene ID: {self.ticket.id}")
        super().save(*args, **kwargs)
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Imagen de Ticket'
        verbose_name_plural = 'Imágenes de Tickets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Imagen de {self.ticket.titulo or 'Ticket'} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
