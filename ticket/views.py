from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timedelta
from categoria.models import Categoria, Subcategoria
from .models import Ticket
from .forms import TicketForm
import json

def is_superuser(user):
    return user.is_superuser

@login_required
def create_ticket(request):
    """Vista para crear un nuevo ticket"""
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.titulo = form.cleaned_data.get('descripcion', '')[:100]  # Primeros 100 caracteres como título
            ticket.save()
            
            # Guardar imágenes si hay alguna
            from .models import TicketImage
            import os
            from django.conf import settings
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            
            print("=" * 80)
            print("🔍 INICIANDO PROCESO DE GUARDADO DE IMÁGENES")
            print("=" * 80)
            
            imagenes = request.FILES.getlist('imagenes')
            urls_imagenes = []
            print(f"📸 Número de imágenes recibidas: {len(imagenes)}")
            
            if len(imagenes) == 0:
                print("⚠️ No hay imágenes para guardar")
            else:
                print(f"📁 MEDIA_ROOT: {settings.MEDIA_ROOT}")
                print(f"📁 MEDIA_URL: {settings.MEDIA_URL}")
                print(f"📁 ¿MEDIA_ROOT existe?: {os.path.exists(settings.MEDIA_ROOT)}")
                
                # Asegurar que el ticket tenga un ID
                print(f"🔍 Verificando ID del ticket...")
                print(f"   - Ticket ID actual: {ticket.id}")
                if not ticket.id:
                    print("   ⚠️ El ticket no tiene ID, guardando primero...")
                    ticket.save()
                    print(f"   ✅ Ticket guardado con ID: {ticket.id}")
                else:
                    print(f"   ✅ Ticket ya tiene ID: {ticket.id}")
                
                ticket_id = ticket.id
                print(f"   ✅ Usando Ticket ID: {ticket_id}")
                
                for idx, imagen in enumerate(imagenes, 1):
                    print(f"\n{'=' * 80}")
                    print(f"📷 PROCESANDO IMAGEN {idx}/{len(imagenes)}")
                    print(f"{'=' * 80}")
                    print(f"   - Nombre: {imagen.name}")
                    print(f"   - Tamaño: {imagen.size} bytes")
                    print(f"   - Tipo: {imagen.content_type}")
                    
                    try:
                        # Generar un nombre único para el archivo
                        import uuid
                        file_extension = os.path.splitext(imagen.name)[1] or '.jpg'
                        unique_filename = f"{uuid.uuid4()}{file_extension}"
                        upload_path = f'tickets/{ticket_id}/imagenes/{unique_filename}'
                        
                        print(f"\n📁 PASO 1: Generando ruta")
                        print(f"   - Ruta relativa: {upload_path}")
                        
                        # Crear la ruta completa
                        full_path = os.path.join(settings.MEDIA_ROOT, upload_path)
                        print(f"   - Ruta completa: {full_path}")
                        
                        # Crear las carpetas si no existen
                        print(f"\n📁 PASO 2: Creando carpetas")
                        dir_path = os.path.dirname(full_path)
                        print(f"   - Directorio a crear: {dir_path}")
                        print(f"   - ¿Directorio existe?: {os.path.exists(dir_path)}")
                        
                        try:
                            os.makedirs(dir_path, exist_ok=True)
                            print(f"   ✅ Carpetas creadas/verificadas: {dir_path}")
                            print(f"   - ¿Directorio existe ahora?: {os.path.exists(dir_path)}")
                        except Exception as e:
                            print(f"   ❌ ERROR al crear carpetas: {str(e)}")
                            raise
                        
                        # Guardar el archivo manualmente
                        print(f"\n💾 PASO 3: Guardando archivo en disco")
                        print(f"   - Ruta destino: {full_path}")
                        
                        try:
                            with open(full_path, 'wb+') as destination:
                                chunk_count = 0
                                for chunk in imagen.chunks():
                                    destination.write(chunk)
                                    chunk_count += 1
                                print(f"   ✅ Archivo escrito ({chunk_count} chunks)")
                        except Exception as e:
                            print(f"   ❌ ERROR al escribir archivo: {str(e)}")
                            raise
                        
                        # Verificar que el archivo se guardó
                        print(f"\n✅ PASO 4: Verificando archivo guardado")
                        if os.path.exists(full_path):
                            file_size = os.path.getsize(full_path)
                            print(f"   ✅ Archivo existe en: {full_path}")
                            print(f"   ✅ Tamaño del archivo: {file_size} bytes")
                            if file_size == 0:
                                print(f"   ⚠️ ADVERTENCIA: El archivo está vacío (0 bytes)")
                        else:
                            print(f"   ❌ ERROR: El archivo NO existe en: {full_path}")
                            raise Exception(f"El archivo no se guardó correctamente en {full_path}")
                        
                        # Crear el objeto TicketImage con la ruta guardada
                        print(f"\n💾 PASO 5: Guardando registro en base de datos")
                        try:
                            ticket_image = TicketImage(ticket=ticket)
                            print(f"   - TicketImage creado (sin guardar aún)")
                            print(f"   - Ticket asignado: {ticket_image.ticket.id}")
                            
                            # Asignar la ruta relativa al campo imagen
                            ticket_image.imagen.name = upload_path
                            print(f"   - Ruta asignada al campo imagen: {ticket_image.imagen.name}")
                            
                            ticket_image.save()
                            print(f"   ✅ TicketImage guardado en BD con ID: {ticket_image.id}")
                        except Exception as e:
                            print(f"   ❌ ERROR al guardar TicketImage en BD: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            raise
                        
                        # Obtener la URL de la imagen
                        print(f"\n🌐 PASO 6: Obteniendo URL de la imagen")
                        try:
                            image_url = ticket_image.imagen.url
                            print(f"   ✅ URL de imagen: {image_url}")
                            urls_imagenes.append(image_url)
                            print(f"   ✅ URL agregada a la lista (total: {len(urls_imagenes)})")
                        except Exception as e:
                            print(f"   ❌ ERROR al obtener URL: {str(e)}")
                            raise
                        
                        print(f"\n✅ IMAGEN {idx} PROCESADA EXITOSAMENTE")
                        
                    except Exception as e:
                        print(f"\n❌ ERROR AL PROCESAR IMAGEN {idx}")
                        print(f"   - Error: {str(e)}")
                        import traceback
                        print("   - Traceback completo:")
                        traceback.print_exc()
                        print(f"\n{'=' * 80}\n")
            
            # Guardar las URLs en el campo imagenes_urls del ticket
            print(f"\n{'=' * 80}")
            print(f"💾 GUARDANDO URLs EN EL TICKET")
            print(f"{'=' * 80}")
            print(f"   - URLs obtenidas: {len(urls_imagenes)}")
            if urls_imagenes:
                for idx, url in enumerate(urls_imagenes, 1):
                    print(f"   {idx}. {url}")
                ticket.imagenes_urls = urls_imagenes
                ticket.save(update_fields=['imagenes_urls'])
                print(f"   ✅ URLs guardadas en ticket.imagenes_urls")
            else:
                print(f"   ⚠️ No hay URLs para guardar")
            
            print(f"\n{'=' * 80}")
            print(f"✅ PROCESO DE GUARDADO DE IMÁGENES COMPLETADO")
            print(f"{'=' * 80}\n")
            
            # Enviar notificación al grupo de Telegram de la sede del ticket
            try:
                from accounts.telegram_utils import send_ticket_notification
                resultado = send_ticket_notification(ticket)
                if resultado:
                    print(f"✅ Notificación enviada para ticket #{ticket.id}")
                else:
                    print(f"⚠️ No se pudo enviar notificación para ticket #{ticket.id} (ver logs arriba)")
            except Exception as e:
                # Si falla la notificación, no es crítico
                import traceback
                print(f"❌ Error crítico enviando notificación de ticket #{ticket.id}: {str(e)}")
                print(f"   Traceback: {traceback.format_exc()}")
            
            messages.success(request, '¡Tu solicitud ha sido enviada correctamente!')
            return redirect('ticket:create_ticket')
        else:
            # Si el formulario no es válido, mostrar los errores
            print("❌ Errores del formulario:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = TicketForm(user=request.user)
    
    categorias = Categoria.objects.filter(activo=True)
    return render(request, 'ticket/create_ticket.html', {'form': form, 'categorias': categorias})

@login_required
def get_subcategorias(request):
    """Vista API para obtener subcategorías por categoría"""
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        subcategorias = Subcategoria.objects.filter(
            categoria_id=categoria_id, 
            activo=True
        ).order_by('nombre')
        data = [{'id': sub.id, 'nombre': sub.nombre} for sub in subcategorias]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@login_required
def get_dependencias(request):
    """Vista API para obtener dependencias por sede"""
    from dependencia.models import Dependencia
    sede_id = request.GET.get('sede')
    if sede_id:
        dependencias = Dependencia.objects.filter(
            sede_id=sede_id, 
            activo=True
        ).order_by('nombre')
        data = [{'id': dep.id, 'nombre': dep.nombre} for dep in dependencias]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@login_required
def get_sedes(request):
    """Vista API para obtener sedes con búsqueda"""
    from sede.models import Sede
    search = request.GET.get('search', '').strip()
    sedes = Sede.objects.filter(activa=True)
    
    if search:
        sedes = sedes.filter(nombre__icontains=search)
    
    sedes = sedes.order_by('nombre')[:50]  # Limitar a 50 resultados
    data = [{'id': sede.id, 'nombre': sede.nombre} for sede in sedes]
    return JsonResponse(data, safe=False)

@login_required
@user_passes_test(is_superuser)
def ticket_admin_list(request):
    """Vista para listar todos los tickets en el admin"""
    from accounts.models import User
    from django.utils import timezone
    
    tickets = Ticket.objects.all().select_related('user', 'sede', 'dependencia', 'categoria', 'subcategoria', 'tecnico')
    
    # Obtener técnicos disponibles (ingenieros de soporte y jefes de soporte)
    tecnicos_disponibles = User.objects.filter(
        rol__in=['ingeniero_soporte', 'jefe_soporte'],
        activo=True,
        is_active=True
    ).order_by('first_name', 'last_name', 'username')
    
    # Estadísticas
    total_tickets = tickets.count()
    pendientes = tickets.filter(estado='pendiente').count()
    en_proceso = tickets.filter(estado='en_proceso').count()
    resueltos = tickets.filter(estado='resuelto').count()
    cerrados = tickets.filter(estado='cerrado').count()
    
    # Preparar datos de tickets con URLs de imágenes para el template
    import json
    tickets_data = {}
    for ticket in tickets:
        imagenes_urls = ticket.get_imagenes_urls() if hasattr(ticket, 'get_imagenes_urls') else []
        tickets_data[str(ticket.id)] = imagenes_urls  # Mantener como lista para JSON
    
    context = {
        'tickets': tickets,
        'tickets_imagenes': json.dumps(tickets_data),  # Convertir todo el diccionario a JSON string
        'tecnicos_disponibles': tecnicos_disponibles,
        'total_tickets': total_tickets,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'resueltos': resueltos,
        'cerrados': cerrados,
    }
    
    return render(request, 'ticket/ticket_admin_list.html', context)

@login_required
def tickets_asignados(request):
    """Vista para listar los tickets asignados al técnico actual"""
    # Filtrar solo tickets asignados al usuario actual y que sea técnico
    if request.user.rol not in ['jefe_soporte', 'ingeniero_soporte']:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('No tienes permiso para acceder a esta página.')
    
    # Obtener filtros de la URL (por defecto 'todos' para mostrar todos los tickets asignados)
    filtro_fecha = request.GET.get('fecha', 'todos')  # hoy, semana, mes, todos
    filtro_estado = request.GET.get('estado', '')
    filtro_prioridad = request.GET.get('prioridad', '')
    
    # Base query: tickets asignados al técnico actual
    tickets = Ticket.objects.filter(
        tecnico=request.user
    ).select_related('user', 'sede', 'dependencia', 'categoria', 'subcategoria', 'tecnico')
    
    # Filtrar por fecha (por defecto, solo del día)
    hoy = timezone.now().date()
    
    if filtro_fecha == 'hoy':
        # Para "hoy", mostrar tickets con fecha_asignacion de hoy O tickets sin fecha_asignacion pero creados hoy
        tickets = tickets.filter(
            Q(fecha_asignacion__isnull=False, fecha_asignacion__date=hoy) |
            Q(fecha_asignacion__isnull=True, created_at__date=hoy)
        )
    elif filtro_fecha == 'semana':
        semana_inicio = hoy - timedelta(days=hoy.weekday())
        tickets = tickets.filter(
            Q(fecha_asignacion__isnull=False, fecha_asignacion__date__gte=semana_inicio) |
            Q(fecha_asignacion__isnull=True, created_at__date__gte=semana_inicio)
        )
    elif filtro_fecha == 'mes':
        mes_inicio = hoy.replace(day=1)
        tickets = tickets.filter(
            Q(fecha_asignacion__isnull=False, fecha_asignacion__date__gte=mes_inicio) |
            Q(fecha_asignacion__isnull=True, created_at__date__gte=mes_inicio)
        )
    # Si es 'todos', no filtramos por fecha
    
    # Filtrar por estado si se especifica
    if filtro_estado:
        tickets = tickets.filter(estado=filtro_estado)
    
    # Filtrar por prioridad si se especifica
    if filtro_prioridad:
        tickets = tickets.filter(prioridad=filtro_prioridad)
    
    # Ordenar por fecha de asignación (primero asignado primero, luego por created_at si no hay fecha_asignacion)
    from django.db.models import F, Case, When
    tickets = tickets.order_by(
        Case(
            When(fecha_asignacion__isnull=False, then=F('fecha_asignacion')),
            default=F('created_at')
        ),
        'created_at'  # Orden secundario por created_at si no hay fecha_asignacion
    )
    
    # Estadísticas (sin filtros aplicados para mostrar totales)
    todos_tickets = Ticket.objects.filter(tecnico=request.user)
    total_tickets = todos_tickets.count()
    pendientes = todos_tickets.filter(estado='pendiente').count()
    en_proceso = todos_tickets.filter(estado='en_proceso').count()
    resueltos = todos_tickets.filter(estado='resuelto').count()
    cerrados = todos_tickets.filter(estado='cerrado').count()
    
    # Preparar datos de tickets para JavaScript de forma segura
    tickets_data = {}
    for ticket in tickets:
        tickets_data[str(ticket.id)] = {
            'id': ticket.id,
            'usuario': ticket.user.username if ticket.user else 'Sin usuario',
            'sede': ticket.sede.nombre if ticket.sede else 'Sin sede',
            'dependencia': ticket.dependencia.nombre if ticket.dependencia else 'Sin dependencia',
            'categoria': ticket.categoria.nombre if ticket.categoria else 'Sin categoría',
            'subcategoria': ticket.subcategoria.nombre if ticket.subcategoria else 'Sin subcategoría',
            'estado': ticket.get_estado_display(),
            'prioridad': ticket.get_prioridad_display(),
            'titulo': ticket.titulo or 'Sin título',
            'descripcion': ticket.descripcion or 'Sin descripción',
        }
    
    context = {
        'tickets': tickets,
        'tickets_data': tickets_data,
        'total_tickets': total_tickets,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'resueltos': resueltos,
        'cerrados': cerrados,
        'filtro_fecha': filtro_fecha,
        'filtro_estado': filtro_estado,
        'filtro_prioridad': filtro_prioridad,
    }
    
    return render(request, 'ticket/tickets_asignados.html', context)

@login_required
@user_passes_test(is_superuser)
def asignar_tecnico(request, ticket_id):
    """Vista API para asignar un técnico a un ticket"""
    from django.utils import timezone
    from django.views.decorators.http import require_http_methods
    
    if request.method == 'POST':
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            tecnico_id = request.POST.get('tecnico_id')
            
            if tecnico_id:
                from accounts.models import User
                tecnico = User.objects.get(
                    id=tecnico_id,
                    rol__in=['ingeniero_soporte', 'jefe_soporte'],
                    activo=True,
                    is_active=True
                )
                ticket.tecnico = tecnico
                ticket.fecha_asignacion = timezone.now()
                
                # Si el ticket está pendiente, cambiar a en_proceso al asignar
                if ticket.estado == 'pendiente':
                    ticket.estado = 'en_proceso'
                
                ticket.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Técnico {tecnico.nombre_completo or tecnico.username} asignado correctamente',
                    'tecnico': {
                        'id': tecnico.id,
                        'username': tecnico.username,
                        'nombre': tecnico.nombre_completo or tecnico.username
                    }
                })
            else:
                # Remover técnico asignado
                ticket.tecnico = None
                ticket.fecha_asignacion = None
                ticket.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Técnico removido correctamente',
                    'tecnico': None
                })
                
        except Ticket.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Ticket no encontrado'
            }, status=404)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Técnico no encontrado o no válido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al asignar técnico: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)

@login_required
@user_passes_test(is_superuser)
def ticket_admin_list_api(request):
    """API endpoint para obtener tickets del admin en formato JSON"""
    from accounts.models import User
    
    tickets = Ticket.objects.all().select_related('user', 'sede', 'dependencia', 'categoria', 'subcategoria', 'tecnico').order_by('-created_at')
    
    # Estadísticas
    total_tickets = tickets.count()
    pendientes = tickets.filter(estado='pendiente').count()
    en_proceso = tickets.filter(estado='en_proceso').count()
    resueltos = tickets.filter(estado='resuelto').count()
    cerrados = tickets.filter(estado='cerrado').count()
    
    # Serializar tickets
    tickets_data = []
    for ticket in tickets:
        # Obtener URLs de imágenes
        imagenes_urls = ticket.get_imagenes_urls() if hasattr(ticket, 'get_imagenes_urls') else []
        
        tickets_data.append({
            'id': ticket.id,
            'usuario': ticket.user.username if ticket.user else 'Sin usuario',
            'sede': ticket.sede.nombre if ticket.sede else 'Sin sede',
            'dependencia': ticket.dependencia.nombre if ticket.dependencia else 'Sin dependencia',
            'categoria': ticket.categoria.nombre if ticket.categoria else 'Sin categoría',
            'subcategoria': ticket.subcategoria.nombre if ticket.subcategoria else 'Sin subcategoría',
            'titulo': ticket.titulo or 'Sin título',
            'descripcion': ticket.descripcion or 'Sin descripción',
            'estado': ticket.estado,
            'estado_display': ticket.get_estado_display(),
            'prioridad': ticket.prioridad,
            'prioridad_display': ticket.get_prioridad_display(),
            'tecnico_id': ticket.tecnico.id if ticket.tecnico else None,
            'tecnico_nombre': (ticket.tecnico.nombre_completo or ticket.tecnico.username) if ticket.tecnico else None,
            'fecha_creacion': ticket.created_at.isoformat() if ticket.created_at else None,
            'fecha_asignacion': ticket.fecha_asignacion.isoformat() if ticket.fecha_asignacion else None,
            'imagenes_urls': imagenes_urls,
        })
    
    return JsonResponse({
        'tickets': tickets_data,
        'stats': {
            'total': total_tickets,
            'pendientes': pendientes,
            'en_proceso': en_proceso,
            'resueltos': resueltos,
            'cerrados': cerrados,
        }
    }, encoder=DjangoJSONEncoder)

@login_required
def tickets_asignados_api(request):
    """API endpoint para obtener tickets asignados en formato JSON"""
    if request.user.rol not in ['jefe_soporte', 'ingeniero_soporte']:
        return JsonResponse({'error': 'No tienes permiso'}, status=403)
    
    # Obtener filtros de la URL
    filtro_fecha = request.GET.get('fecha', 'todos')
    filtro_estado = request.GET.get('estado', '')
    filtro_prioridad = request.GET.get('prioridad', '')
    
    # Base query: tickets asignados al técnico actual
    tickets = Ticket.objects.filter(
        tecnico=request.user
    ).select_related('user', 'sede', 'dependencia', 'categoria', 'subcategoria', 'tecnico')
    
    # Filtrar por fecha
    hoy = timezone.now().date()
    
    if filtro_fecha == 'hoy':
        tickets = tickets.filter(
            Q(fecha_asignacion__isnull=False, fecha_asignacion__date=hoy) |
            Q(fecha_asignacion__isnull=True, created_at__date=hoy)
        )
    elif filtro_fecha == 'semana':
        semana_inicio = hoy - timedelta(days=hoy.weekday())
        tickets = tickets.filter(
            Q(fecha_asignacion__isnull=False, fecha_asignacion__date__gte=semana_inicio) |
            Q(fecha_asignacion__isnull=True, created_at__date__gte=semana_inicio)
        )
    elif filtro_fecha == 'mes':
        mes_inicio = hoy.replace(day=1)
        tickets = tickets.filter(
            Q(fecha_asignacion__isnull=False, fecha_asignacion__date__gte=mes_inicio) |
            Q(fecha_asignacion__isnull=True, created_at__date__gte=mes_inicio)
        )
    
    # Filtrar por estado
    if filtro_estado:
        tickets = tickets.filter(estado=filtro_estado)
    
    # Filtrar por prioridad
    if filtro_prioridad:
        tickets = tickets.filter(prioridad=filtro_prioridad)
    
    # Ordenar
    from django.db.models import F, Case, When
    tickets = tickets.order_by(
        Case(
            When(fecha_asignacion__isnull=False, then=F('fecha_asignacion')),
            default=F('created_at')
        ),
        'created_at'
    )
    
    # Estadísticas (sin filtros)
    todos_tickets = Ticket.objects.filter(tecnico=request.user)
    total_tickets = todos_tickets.count()
    pendientes = todos_tickets.filter(estado='pendiente').count()
    en_proceso = todos_tickets.filter(estado='en_proceso').count()
    resueltos = todos_tickets.filter(estado='resuelto').count()
    cerrados = todos_tickets.filter(estado='cerrado').count()
    
    # Serializar tickets
    tickets_data = []
    for ticket in tickets:
        # Obtener URLs de imágenes
        imagenes_urls = ticket.get_imagenes_urls() if hasattr(ticket, 'get_imagenes_urls') else []
        
        tickets_data.append({
            'id': ticket.id,
            'usuario': ticket.user.username if ticket.user else 'Sin usuario',
            'sede': ticket.sede.nombre if ticket.sede else 'Sin sede',
            'dependencia': ticket.dependencia.nombre if ticket.dependencia else 'Sin dependencia',
            'categoria': ticket.categoria.nombre if ticket.categoria else 'Sin categoría',
            'subcategoria': ticket.subcategoria.nombre if ticket.subcategoria else 'Sin subcategoría',
            'titulo': ticket.titulo or 'Sin título',
            'descripcion': ticket.descripcion or 'Sin descripción',
            'estado': ticket.estado,
            'estado_display': ticket.get_estado_display(),
            'prioridad': ticket.prioridad,
            'prioridad_display': ticket.get_prioridad_display(),
            'fecha_creacion': ticket.created_at.isoformat() if ticket.created_at else None,
            'fecha_asignacion': ticket.fecha_asignacion.isoformat() if ticket.fecha_asignacion else None,
            'imagenes_urls': imagenes_urls,
        })
    
    return JsonResponse({
        'tickets': tickets_data,
        'stats': {
            'total': total_tickets,
            'pendientes': pendientes,
            'en_proceso': en_proceso,
            'resueltos': resueltos,
            'cerrados': cerrados,
        }
    }, encoder=DjangoJSONEncoder)

@login_required
def mis_tickets(request):
    """Vista para listar los tickets creados por el usuario actual"""
    # Obtener filtros de la URL (por defecto 'todos' para mostrar todos los tickets)
    filtro_fecha = request.GET.get('fecha', 'todos')  # hoy, semana, mes, todos
    filtro_estado = request.GET.get('estado', '')
    filtro_prioridad = request.GET.get('prioridad', '')
    
    # Base query: tickets creados por el usuario actual
    tickets = Ticket.objects.filter(
        user=request.user
    ).select_related('user', 'sede', 'dependencia', 'categoria', 'subcategoria', 'tecnico')
    
    # Filtrar por fecha
    hoy = timezone.now().date()
    
    if filtro_fecha == 'hoy':
        tickets = tickets.filter(created_at__date=hoy)
    elif filtro_fecha == 'semana':
        semana_inicio = hoy - timedelta(days=hoy.weekday())
        tickets = tickets.filter(created_at__date__gte=semana_inicio)
    elif filtro_fecha == 'mes':
        mes_inicio = hoy.replace(day=1)
        tickets = tickets.filter(created_at__date__gte=mes_inicio)
    # Si es 'todos', no filtramos por fecha
    
    # Filtrar por estado si se especifica
    if filtro_estado:
        tickets = tickets.filter(estado=filtro_estado)
    
    # Filtrar por prioridad si se especifica
    if filtro_prioridad:
        tickets = tickets.filter(prioridad=filtro_prioridad)
    
    # Ordenar por fecha de creación (más recientes primero)
    tickets = tickets.order_by('-created_at')
    
    # Estadísticas (sin filtros aplicados para mostrar totales)
    todos_tickets = Ticket.objects.filter(user=request.user)
    total_tickets = todos_tickets.count()
    pendientes = todos_tickets.filter(estado='pendiente').count()
    en_proceso = todos_tickets.filter(estado='en_proceso').count()
    resueltos = todos_tickets.filter(estado='resuelto').count()
    cerrados = todos_tickets.filter(estado='cerrado').count()
    
    # Preparar datos de tickets para JavaScript de forma segura
    tickets_data = {}
    for ticket in tickets:
        # Obtener URLs de imágenes
        imagenes_urls = ticket.get_imagenes_urls() if hasattr(ticket, 'get_imagenes_urls') else []
        
        tickets_data[str(ticket.id)] = {
            'id': ticket.id,
            'usuario': ticket.user.username if ticket.user else 'Sin usuario',
            'sede': ticket.sede.nombre if ticket.sede else 'Sin sede',
            'dependencia': ticket.dependencia.nombre if ticket.dependencia else 'Sin dependencia',
            'categoria': ticket.categoria.nombre if ticket.categoria else 'Sin categoría',
            'subcategoria': ticket.subcategoria.nombre if ticket.subcategoria else 'Sin subcategoría',
            'estado': ticket.get_estado_display(),
            'prioridad': ticket.get_prioridad_display(),
            'titulo': ticket.titulo or 'Sin título',
            'descripcion': ticket.descripcion or 'Sin descripción',
            'tecnico': ticket.tecnico.nombre_completo if ticket.tecnico and hasattr(ticket.tecnico, 'nombre_completo') else (ticket.tecnico.username if ticket.tecnico else 'Sin técnico asignado'),
            'imagenes_urls': imagenes_urls,
        }
    
    context = {
        'tickets': tickets,
        'tickets_data': tickets_data,
        'total_tickets': total_tickets,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'resueltos': resueltos,
        'cerrados': cerrados,
        'filtro_fecha': filtro_fecha,
        'filtro_estado': filtro_estado,
        'filtro_prioridad': filtro_prioridad,
    }
    
    return render(request, 'ticket/mis_tickets.html', context)
