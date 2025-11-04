"""
Utilidades para integración con Telegram Bot
"""
import os
import requests
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()


def get_bot_token():
    """Obtiene el token del bot desde las variables de entorno"""
    return os.getenv('TELEGRAM_BOT_TOKEN', '')


def get_api_base(bot_token=None):
    """Obtiene la URL base de la API de Telegram"""
    if not bot_token:
        bot_token = get_bot_token()
    return f"https://api.telegram.org/bot{bot_token}"


def check_response(r):
    """Verifica la respuesta de la API de Telegram"""
    try:
        j = r.json()
    except Exception:
        r.raise_for_status()
    if not j.get("ok"):
        raise RuntimeError(f"Telegram API error: {j}")
    return j


def get_updates(api_base, limit=10, offset=None, timeout=1):
    """Obtiene actualizaciones del bot"""
    params = {"limit": limit, "timeout": timeout}
    if offset:
        params["offset"] = offset
    r = requests.get(f"{api_base}/getUpdates", params=params, timeout=15)
    return check_response(r).get("result", [])


def get_last_chat_id(api_base, dni=None):
    """
    Obtiene el último chat_id de las actualizaciones
    Si se proporciona DNI, busca mensajes que contengan ese DNI
    """
    updates = get_updates(api_base, limit=100)
    if not updates:
        return None, updates
    
    # Si hay DNI, buscar mensajes que contengan ese DNI
    if dni:
        for u in reversed(updates):
            msg = u.get("message") or u.get("edited_message")
            if not msg:
                continue
            text = msg.get("text", "")
            if dni in text:
                chat = msg.get("chat")
                if chat and "id" in chat:
                    return chat["id"], updates
    
    # Si no hay DNI o no se encontró, devolver el último chat
    for u in reversed(updates):
        msg = u.get("message") or u.get("edited_message") or u.get("channel_post")
        if not msg:
            continue
        chat = msg.get("chat")
        if chat and "id" in chat:
            return chat["id"], updates
    
    return None, updates


def send_text(api_base, chat_id, text):
    """Envía un mensaje de texto"""
    payload = {"chat_id": chat_id, "text": text}
    r = requests.post(f"{api_base}/sendMessage", json=payload, timeout=30)
    return check_response(r)


def send_document_url(api_base, chat_id, url, caption=""):
    """Envía un documento desde una URL"""
    payload = {"chat_id": chat_id, "caption": caption, "document": url}
    r = requests.post(f"{api_base}/sendDocument", json=payload, timeout=60)
    j = r.json()
    if not j.get("ok"):
        try:
            rr = requests.get(url, stream=True, timeout=30)
            rr.raise_for_status()
            files = {"document": ("file.pdf", rr.raw)}
            r2 = requests.post(
                f"{api_base}/sendDocument",
                data={"chat_id": chat_id, "caption": caption},
                files=files,
                timeout=120
            )
            return check_response(r2)
        except Exception as e:
            raise RuntimeError(f"Error al enviar documento: {e} | resp inicial: {j}")
    return j


def get_chat_info(api_base, chat_id):
    """Obtiene información de un chat"""
    r = requests.get(f"{api_base}/getChat", params={"chat_id": chat_id}, timeout=30)
    return check_response(r)


def delete_webhook(api_base):
    """Elimina el webhook si existe"""
    r = requests.post(f"{api_base}/deleteWebhook")
    return check_response(r)


def send_notification_to_group(api_base, grupo_chat_id, message):
    """Envía una notificación a un grupo de Telegram"""
    try:
        payload = {"chat_id": grupo_chat_id, "text": message, "parse_mode": "HTML"}
        r = requests.post(f"{api_base}/sendMessage", json=payload, timeout=30)
        return check_response(r)
    except RuntimeError as e:
        # Manejar error de migración de grupo a supergroup
        error_str = str(e)
        if "group chat was upgraded to a supergroup chat" in error_str or "migrate_to_chat_id" in error_str:
            # Extraer el nuevo chat_id del error
            import re
            import json as json_module
            try:
                # Intentar extraer el diccionario del error
                # El formato del error es: "Telegram API error: {'ok': False, 'error_code': 400, ...}"
                # Buscar el diccionario completo
                match = re.search(r"\{.*'parameters':\s*\{.*?'migrate_to_chat_id':\s*(-?\d+).*?\}", error_str)
                if not match:
                    # Buscar solo el migrate_to_chat_id
                    match = re.search(r"'migrate_to_chat_id':\s*(-?\d+)", error_str)
                
                if match:
                    nuevo_chat_id = match.group(1)
                    print(f"⚠️ [Telegram] El grupo {grupo_chat_id} fue migrado a supergroup. Nuevo Chat ID: {nuevo_chat_id}")
                    # Intentar enviar con el nuevo chat_id
                    try:
                        payload = {"chat_id": nuevo_chat_id, "text": message, "parse_mode": "HTML"}
                        r = requests.post(f"{api_base}/sendMessage", json=payload, timeout=30)
                        result = check_response(r)
                        # Retornar el nuevo chat_id para actualizar la BD
                        if result:
                            result['_new_chat_id'] = str(nuevo_chat_id)
                        return result
                    except Exception as e2:
                        print(f"❌ [Telegram] Error al enviar con nuevo Chat ID {nuevo_chat_id}: {str(e2)}")
                        # Retornar el nuevo chat_id aunque falle el envío para que se actualice
                        return {'_new_chat_id': str(nuevo_chat_id), '_error': str(e2)}
                else:
                    print(f"⚠️ [Telegram] No se pudo extraer el nuevo Chat ID del error: {error_str}")
            except Exception as parse_error:
                print(f"⚠️ [Telegram] Error parseando migración: {str(parse_error)}")
        # Re-lanzar el error original si no es de migración
        print(f"Error enviando notificación a grupo {grupo_chat_id}: {str(e)}")
        return None
    except Exception as e:
        # Log error pero no romper el flujo
        print(f"Error enviando notificación a grupo {grupo_chat_id}: {str(e)}")
        return None


def send_ticket_notification(ticket):
    """
    Envía notificación cuando se crea un ticket al grupo de la sede del ticket
    """
    from accounts.models import TelegramGrupoSede
    
    try:
        # Verificar que el ticket tenga sede
        if not ticket.sede:
            print(f"⚠️ [Telegram] Ticket #{ticket.id}: No tiene sede asignada")
            return False
        
        print(f"📋 [Telegram] Ticket #{ticket.id}: Buscando grupo para sede '{ticket.sede.nombre}'")
        
        # Obtener API base
        api_base = get_api_base()
        if not api_base:
            print(f"❌ [Telegram] Ticket #{ticket.id}: Bot Token no configurado en .env")
            return False
        
        # Buscar grupo de Telegram para la sede del ticket
        try:
            grupo = TelegramGrupoSede.objects.get(sede=ticket.sede, activo=True)
            print(f"✅ [Telegram] Ticket #{ticket.id}: Grupo encontrado - Chat ID: {grupo.grupo_chat_id}")
        except TelegramGrupoSede.DoesNotExist:
            # No hay grupo configurado para esta sede
            print(f"⚠️ [Telegram] Ticket #{ticket.id}: No hay grupo configurado para la sede '{ticket.sede.nombre}'")
            print(f"   💡 Solución: Configura un grupo de Telegram para '{ticket.sede.nombre}' en /accounts/telegram-grupos/")
            return False
        
        # Obtener información del usuario
        usuario_nombre = ticket.user.get_full_name() if ticket.user.get_full_name() else ticket.user.username
        if hasattr(ticket.user, 'nombre_completo') and ticket.user.nombre_completo:
            usuario_nombre = ticket.user.nombre_completo
        elif hasattr(ticket.user, 'nombres') and ticket.user.nombres:
            usuario_nombre = f"{ticket.user.nombres} {ticket.user.apellidos_paterno or ''} {ticket.user.apellidos_materno or ''}".strip()
        
        # Obtener título y descripción
        titulo = ticket.titulo if ticket.titulo else 'Sin título'
        descripcion = ticket.descripcion if ticket.descripcion else 'Sin descripción'
        
        # Obtener categoría completa
        categoria_completa = ''
        if ticket.categoria:
            categoria_completa = ticket.categoria.nombre
            if ticket.subcategoria:
                categoria_completa += f" - {ticket.subcategoria.nombre}"
        else:
            categoria_completa = 'Sin categoría'
        
        # Obtener información del técnico si está asignado
        tecnico_info = ''
        if ticket.tecnico:
            if hasattr(ticket.tecnico, 'nombre_completo') and ticket.tecnico.nombre_completo:
                tecnico_info = f"👷 <b>Técnico:</b> {ticket.tecnico.nombre_completo}"
            else:
                tecnico_info = f"👷 <b>Técnico:</b> {ticket.tecnico.username}"
        else:
            tecnico_info = "👷 <b>Técnico:</b> Sin asignar"
        
        # Iconos según prioridad
        prioridad_iconos = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🟠',
            'urgente': '🔴'
        }
        prioridad_icono = prioridad_iconos.get(ticket.prioridad, '⚪')
        
        # Iconos según estado
        estado_iconos = {
            'pendiente': '⏳',
            'en_proceso': '🔄',
            'resuelto': '✅',
            'cerrado': '🔒'
        }
        estado_icono = estado_iconos.get(ticket.estado, '📋')
        
        # Crear mensaje de notificación formateado similar a la card
        mensaje = f"""
🎫 <b>NUEVO TICKET CREADO</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 <b>Ticket #{ticket.id}</b>

👤 <b>Usuario:</b> {usuario_nombre}
🏢 <b>Sede:</b> {ticket.sede.nombre if ticket.sede else 'Sin sede'}
📁 <b>Dependencia:</b> {ticket.dependencia.nombre if ticket.dependencia else 'Sin dependencia'}

📂 <b>Categoría:</b> {categoria_completa}

📝 <b>Título:</b>
{titulo[:100]}{'...' if titulo and len(titulo) > 100 else ''}

📄 <b>Descripción:</b>
{descripcion[:300]}{'...' if descripcion and len(descripcion) > 300 else ''}

{prioridad_icono} <b>Prioridad:</b> {ticket.get_prioridad_display()}
{estado_icono} <b>Estado:</b> {ticket.get_estado_display()}

{tecnico_info}

⏰ <b>Fecha de Creación:</b> {ticket.created_at.strftime('%d/%m/%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
        
        # Enviar notificación al grupo
        print(f"📤 [Telegram] Ticket #{ticket.id}: Enviando notificación al grupo {grupo.grupo_chat_id}...")
        result = send_notification_to_group(api_base, grupo.grupo_chat_id, mensaje)
        
        if result is not None:
            # Si el grupo fue migrado a supergroup, actualizar el Chat ID en la BD
            if '_new_chat_id' in result:
                nuevo_chat_id = result['_new_chat_id']
                print(f"🔄 [Telegram] Ticket #{ticket.id}: Grupo migrado. Actualizando Chat ID de {grupo.grupo_chat_id} a {nuevo_chat_id}")
                grupo.grupo_chat_id = nuevo_chat_id
                grupo.save()
                print(f"✅ [Telegram] Ticket #{ticket.id}: Chat ID actualizado en la base de datos")
            
            print(f"✅ [Telegram] Ticket #{ticket.id}: Notificación enviada exitosamente")
            return True
        else:
            print(f"❌ [Telegram] Ticket #{ticket.id}: Error al enviar notificación (resultado None)")
            return False
        
    except Exception as e:
        # Log error pero no romper el flujo
        import traceback
        print(f"❌ [Telegram] Ticket #{ticket.id}: Error enviando notificación: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

