from django.urls import path
from . import views

app_name = 'categoria'

urlpatterns = [
    # URLs para Categorías
    path('', views.categoria_list, name='list'),
    path('create/', views.categoria_create, name='create'),
    path('<int:pk>/edit/', views.categoria_edit, name='edit'),
    path('<int:pk>/delete/', views.categoria_delete, name='delete'),
    
    # URLs para Subcategorías
    path('subcategoria/', views.subcategoria_list, name='subcategoria_list'),
    path('subcategoria/create/', views.subcategoria_create, name='subcategoria_create'),
    path('subcategoria/<int:pk>/edit/', views.subcategoria_edit, name='subcategoria_edit'),
    path('subcategoria/<int:pk>/delete/', views.subcategoria_delete, name='subcategoria_delete'),
]

