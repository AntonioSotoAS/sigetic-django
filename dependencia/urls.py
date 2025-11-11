from django.urls import path
from . import views

app_name = 'dependencia'

urlpatterns = [
    path('', views.dependencia_list, name='list'),
    path('create/', views.dependencia_create, name='create'),
    path('<int:pk>/edit/', views.dependencia_edit, name='edit'),
    path('<int:pk>/delete/', views.dependencia_delete, name='delete'),
    path('upload-excel/', views.dependencia_upload_excel, name='upload_excel'),
    path('download-template/', views.dependencia_download_template, name='download_template'),
]
