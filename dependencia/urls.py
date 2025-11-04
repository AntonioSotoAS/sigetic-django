from django.urls import path
from . import views

app_name = 'dependencia'

urlpatterns = [
    path('', views.dependencia_list, name='list'),
    path('create/', views.dependencia_create, name='create'),
    path('<int:pk>/edit/', views.dependencia_edit, name='edit'),
    path('<int:pk>/delete/', views.dependencia_delete, name='delete'),
]
