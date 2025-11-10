#!/usr/bin/env python
"""
Passenger WSGI entry point for SIGETIC project.

This file is used by Passenger to serve the Django application.
Make sure to configure Passenger to use this file as the entry point.
"""

import os
import sys

# Obtener el directorio del proyecto (donde está este archivo)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Agregar el directorio del proyecto al PYTHONPATH
# Esto permite que Python encuentre el módulo 'sigetic'
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Configurar el módulo de settings de Django
# IMPORTANTE: FORZAR 'sigetic.settings' (sobrescribe cualquier variable de entorno)
# NO usar setdefault porque puede haber una variable de entorno incorrecta
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigetic.settings'

# Importar y configurar la aplicación WSGI de Django
from django.core.wsgi import get_wsgi_application

# Crear la aplicación WSGI
application = get_wsgi_application()

