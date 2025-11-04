from django.urls import path
from . import views

app_name = 'cargo'

urlpatterns = [
    path('', views.cargo_list, name='list'),
    path('create/', views.cargo_create, name='create'),
    path('<int:pk>/edit/', views.cargo_edit, name='edit'),
    path('<int:pk>/delete/', views.cargo_delete, name='delete'),
]
