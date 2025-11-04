from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """Vista de bienvenida después del login"""
    context = {
        'user': request.user,
    }
    return render(request, 'core/dashboard.html', context)
