from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.user_list, name='list'),
    path('create/', views.user_create, name='create'),
    path('<int:pk>/edit/', views.user_edit, name='edit'),
    path('<int:pk>/delete/', views.user_delete, name='delete'),
    
    # URLs para Telegram Bot
    path('vincular-bot/', views.vincular_bot, name='vincular_bot'),
    path('desvincular-bot/', views.desvincular_bot, name='desvincular_bot'),
    path('obtener-chat-id/', views.obtener_chat_id, name='obtener_chat_id'),
    
    # URLs para grupos de Telegram por sede
    path('telegram-grupos/', views.telegram_grupos_list, name='telegram_grupos_list'),
    path('telegram-grupos/create/', views.telegram_grupo_create, name='telegram_grupo_create'),
    path('telegram-grupos/<int:pk>/edit/', views.telegram_grupo_edit, name='telegram_grupo_edit'),
    path('telegram-grupos/<int:pk>/delete/', views.telegram_grupo_delete, name='telegram_grupo_delete'),
    path('telegram-grupos/obtener-chat-id/', views.obtener_grupo_chat_id, name='obtener_grupo_chat_id'),
]
