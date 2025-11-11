from django.urls import path
from . import views

app_name = 'sede'

urlpatterns = [
    path('', views.sede_list, name='list'),
    path('create/', views.sede_create, name='create'),
    path('<int:pk>/edit/', views.sede_edit, name='edit'),
    path('<int:pk>/delete/', views.sede_delete, name='delete'),
    path('upload-excel/', views.sede_upload_excel, name='upload_excel'),
    path('download-template/', views.sede_download_template, name='download_template'),
]

