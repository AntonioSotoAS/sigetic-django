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
    
    context = {
        'tickets': tickets,
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
