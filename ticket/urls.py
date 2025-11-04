from django.urls import path
from . import views

app_name = 'ticket'

urlpatterns = [
    path('create/', views.create_ticket, name='create_ticket'),
    path('mis-tickets/', views.mis_tickets, name='mis_tickets'),
    path('asignados/', views.tickets_asignados, name='tickets_asignados'),
    path('admin/', views.ticket_admin_list, name='ticket_admin_list'),
    path('api/subcategorias/', views.get_subcategorias, name='get_subcategorias'),
    path('api/dependencias/', views.get_dependencias, name='get_dependencias'),
    path('admin/<int:ticket_id>/asignar-tecnico/', views.asignar_tecnico, name='asignar_tecnico'),
    path('api/admin/list/', views.ticket_admin_list_api, name='ticket_admin_list_api'),
    path('api/asignados/', views.tickets_asignados_api, name='tickets_asignados_api'),
]

