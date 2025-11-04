from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Sede
from .forms import SedeForm

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def sede_list(request):
    """Lista todas las sedes"""
    sedes = Sede.objects.all()
    return render(request, 'sede/sede_list.html', {'sedes': sedes})

@login_required
@user_passes_test(is_superuser)
def sede_create(request):
    """Crear nueva sede"""
    if request.method == 'POST':
        form = SedeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sede creada exitosamente.')
            return redirect('sede:list')
    else:
        form = SedeForm()
    return render(request, 'sede/sede_form.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(is_superuser)
def sede_edit(request, pk):
    """Editar sede existente"""
    sede = get_object_or_404(Sede, pk=pk)
    if request.method == 'POST':
        form = SedeForm(request.POST, instance=sede)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sede actualizada exitosamente.')
            return redirect('sede:list')
    else:
        form = SedeForm(instance=sede)
    return render(request, 'sede/sede_form.html', {'form': form, 'sede': sede, 'action': 'Editar'})

@login_required
@user_passes_test(is_superuser)
def sede_delete(request, pk):
    """Eliminar sede"""
    sede = get_object_or_404(Sede, pk=pk)
    if request.method == 'POST':
        sede.delete()
        messages.success(request, 'Sede eliminada exitosamente.')
        return redirect('sede:list')
    return render(request, 'sede/sede_confirm_delete.html', {'sede': sede})
