from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Dependencia
from .forms import DependenciaForm

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def dependencia_list(request):
    """Lista todas las dependencias"""
    dependencias = Dependencia.objects.all()
    return render(request, 'dependencia/dependencia_list.html', {'dependencias': dependencias})

@login_required
@user_passes_test(is_superuser)
def dependencia_create(request):
    """Crear nueva dependencia"""
    if request.method == 'POST':
        form = DependenciaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dependencia creada exitosamente.')
            return redirect('dependencia:list')
    else:
        form = DependenciaForm()
    return render(request, 'dependencia/dependencia_form.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(is_superuser)
def dependencia_edit(request, pk):
    """Editar dependencia existente"""
    dependencia = get_object_or_404(Dependencia, pk=pk)
    if request.method == 'POST':
        form = DependenciaForm(request.POST, instance=dependencia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dependencia actualizada exitosamente.')
            return redirect('dependencia:list')
    else:
        form = DependenciaForm(instance=dependencia)
    return render(request, 'dependencia/dependencia_form.html', {'form': form, 'dependencia': dependencia, 'action': 'Editar'})

@login_required
@user_passes_test(is_superuser)
def dependencia_delete(request, pk):
    """Eliminar dependencia"""
    dependencia = get_object_or_404(Dependencia, pk=pk)
    if request.method == 'POST':
        dependencia.delete()
        messages.success(request, 'Dependencia eliminada exitosamente.')
        return redirect('dependencia:list')
    return render(request, 'dependencia/dependencia_confirm_delete.html', {'dependencia': dependencia})