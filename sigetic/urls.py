"""
URL configuration for sigetic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('login/', include('login.urls', namespace='login')),
    path('ticket/', include('ticket.urls', namespace='ticket')),
    path('sede/', include('sede.urls', namespace='sede')),
    path('categoria/', include('categoria.urls', namespace='categoria')),
    path('cargo/', include('cargo.urls', namespace='cargo')),
    path('dependencia/', include('dependencia.urls', namespace='dependencia')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()  # Busca en STATICFILES_DIRS y en cada app
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
