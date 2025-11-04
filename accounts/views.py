from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import User, TelegramGrupoSede
from .forms import UserForm, UserCreateForm
from .telegram_utils import (
    get_api_base, get_last_chat_id, send_text, 
    get_chat_info, delete_webhook, get_updates
)

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def user_list(request):
    """Lista todos los usuarios"""
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@user_passes_test(is_superuser)
def user_create(request):
    """Crear nuevo usuario"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('accounts:list')
    else:
        form = UserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(is_superuser)
def user_edit(request, pk):
    """Editar usuario existente"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('accounts:list')
    else:
        form = UserForm(instance=user)
    return render(request, 'accounts/user_form.html', {'form': form, 'user': user, 'action': 'Editar'})

@login_required
@user_passes_test(is_superuser)
def user_delete(request, pk):
    """Eliminar usuario"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
        return redirect('accounts:list')
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})

# Vistas para Telegram Bot
@login_required
def vincular_bot(request):
    """Vista para vincular el bot de Telegram al usuario actual"""
    user = request.user
    
    if request.method == 'POST':
        try:
            api_base = get_api_base()
            if not api_base:
                messages.error(request, 'Bot Token no configurado. Contacta al administrador.')
                return redirect('accounts:vincular_bot')
            
            # Obtener chat_id usando el DNI del usuario
            dni = user.dni
            if not dni:
                messages.error(request, 'Debes tener un DNI registrado para vincular el bot.')
                return redirect('accounts:vincular_bot')
            
            chat_id, updates = get_last_chat_id(api_base, dni=dni)
            
            if not chat_id:
                messages.warning(
                    request, 
                    f'No se encontró tu chat_id. Envía un mensaje al bot con tu DNI: {dni}'
                )
                return redirect('accounts:vincular_bot')
            
            # Verificar que el chat_id no esté usado por otro usuario
            if User.objects.filter(telegram_chat_id=chat_id).exclude(id=user.id).exists():
                messages.error(request, 'Este chat_id ya está vinculado a otro usuario.')
                return redirect('accounts:vincular_bot')
            
            # Guardar chat_id y vincular bot
            user.telegram_chat_id = str(chat_id)
            user.bot_vinculado = True
            user.save()
            
            # Enviar mensaje de confirmación
            try:
                send_text(api_base, chat_id, f'✅ Bot vinculado exitosamente para {user.nombre_completo}')
            except:
                pass  # Si falla el envío, no es crítico
            
            messages.success(request, 'Bot vinculado exitosamente.')
            return redirect('accounts:vincular_bot')
            
        except Exception as e:
            messages.error(request, f'Error al vincular bot: {str(e)}')
            return redirect('accounts:vincular_bot')
    
    # GET: Mostrar estado del bot
    context = {
        'bot_vinculado': user.bot_vinculado,
        'telegram_chat_id': user.telegram_chat_id,
        'dni': user.dni,
    }
    return render(request, 'accounts/vincular_bot.html', context)


@login_required
def desvincular_bot(request):
    """Vista para desvincular el bot de Telegram"""
    user = request.user
    
    if request.method == 'POST':
        user.bot_vinculado = False
        user.telegram_chat_id = None
        user.save()
        messages.success(request, 'Bot desvinculado exitosamente.')
        return redirect('accounts:vincular_bot')
    
    return redirect('accounts:vincular_bot')


@login_required
def obtener_chat_id(request):
    """API para obtener chat_id (AJAX)"""
    if request.method == 'POST':
        try:
            api_base = get_api_base()
            if not api_base:
                return JsonResponse({'error': 'Bot Token no configurado'}, status=400)
            
            dni = request.user.dni
            if not dni:
                return JsonResponse({'error': 'DNI no registrado'}, status=400)
            
            chat_id, updates = get_last_chat_id(api_base, dni=dni)
            
            if chat_id:
                return JsonResponse({
                    'success': True,
                    'chat_id': str(chat_id),
                    'message': 'Chat ID encontrado'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró chat_id. Envía un mensaje al bot con tu DNI: {dni}'
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vistas para gestión de grupos de Telegram por sede
@login_required
@user_passes_test(is_superuser)
def telegram_grupos_list(request):
    """Lista todos los grupos de Telegram por sede"""
    from sede.models import Sede
    
    grupos = TelegramGrupoSede.objects.select_related('sede').all()
    sedes_sin_grupo = Sede.objects.filter(activa=True).exclude(
        telegram_grupo__isnull=False
    )
    
    context = {
        'grupos': grupos,
        'sedes_sin_grupo': sedes_sin_grupo,
    }
    return render(request, 'accounts/telegram_grupos_list.html', context)


@login_required
@user_passes_test(is_superuser)
def telegram_grupo_create(request):
    """Crear grupo de Telegram para una sede"""
    from sede.models import Sede
    
    if request.method == 'POST':
        sede_id = request.POST.get('sede')
        grupo_chat_id = request.POST.get('grupo_chat_id')
        nombre_grupo = request.POST.get('nombre_grupo', '')
        
        if not sede_id or not grupo_chat_id:
            messages.error(request, 'Sede y Chat ID son requeridos.')
            return redirect('accounts:telegram_grupos_list')
        
        sede = get_object_or_404(Sede, id=sede_id)
        
        # Verificar que la sede no tenga ya un grupo
        if TelegramGrupoSede.objects.filter(sede=sede).exists():
            messages.error(request, f'La sede {sede.nombre} ya tiene un grupo asignado.')
            return redirect('accounts:telegram_grupos_list')
        
        # Crear grupo
        grupo = TelegramGrupoSede.objects.create(
            sede=sede,
            grupo_chat_id=grupo_chat_id,
            nombre_grupo=nombre_grupo
        )
        
        messages.success(request, f'Grupo creado exitosamente para {sede.nombre}.')
        return redirect('accounts:telegram_grupos_list')
    
    return redirect('accounts:telegram_grupos_list')


@login_required
@user_passes_test(is_superuser)
def telegram_grupo_delete(request, pk):
    """Eliminar grupo de Telegram"""
    grupo = get_object_or_404(TelegramGrupoSede, pk=pk)
    
    if request.method == 'POST':
        sede_nombre = grupo.sede.nombre
        grupo.delete()
        messages.success(request, f'Grupo eliminado exitosamente para {sede_nombre}.')
        return redirect('accounts:telegram_grupos_list')
    
    return render(request, 'accounts/telegram_grupo_confirm_delete.html', {'grupo': grupo})


@login_required
@user_passes_test(is_superuser)
def obtener_grupo_chat_id(request):
    """API para obtener el chat_id de un grupo desde las actualizaciones del bot"""
    if request.method == 'POST':
        try:
            api_base = get_api_base()
            if not api_base:
                return JsonResponse({'error': 'Bot Token no configurado'}, status=400)
            
            # Obtener las últimas actualizaciones
            updates = get_updates(api_base, limit=50)
            
            # Buscar grupos en las actualizaciones
            grupos_encontrados = []
            for update in reversed(updates):
                msg = update.get("message") or update.get("edited_message")
                if not msg:
                    continue
                
                chat = msg.get("chat")
                if chat and chat.get("type") == "group" and "id" in chat:
                    chat_id = chat["id"]
                    nombre_grupo = chat.get("title", "Sin nombre")
                    
                    # Evitar duplicados
                    if not any(g["chat_id"] == str(chat_id) for g in grupos_encontrados):
                        grupos_encontrados.append({
                            "chat_id": str(chat_id),
                            "nombre": nombre_grupo,
                            "username": chat.get("username", ""),
                        })
            
            if grupos_encontrados:
                return JsonResponse({
                    'success': True,
                    'grupos': grupos_encontrados,
                    'message': f'Se encontraron {len(grupos_encontrados)} grupo(s)'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No se encontraron grupos. Asegúrate de que el bot esté en el grupo y que alguien haya enviado un mensaje recientemente.'
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)