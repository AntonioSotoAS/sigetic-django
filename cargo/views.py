from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Cargo
from .forms import CargoForm

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def cargo_list(request):
    """Lista todos los cargos"""
    cargos = Cargo.objects.all()
    return render(request, 'cargo/cargo_list.html', {'cargos': cargos})

@login_required
@user_passes_test(is_superuser)
def cargo_create(request):
    """Crear nuevo cargo"""
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo creado exitosamente.')
            return redirect('cargo:list')
    else:
        form = CargoForm()
    return render(request, 'cargo/cargo_form.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(is_superuser)
def cargo_edit(request, pk):
    """Editar cargo existente"""
    cargo = get_object_or_404(Cargo, pk=pk)
    if request.method == 'POST':
        form = CargoForm(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo actualizado exitosamente.')
            return redirect('cargo:list')
    else:
        form = CargoForm(instance=cargo)
    return render(request, 'cargo/cargo_form.html', {'form': form, 'cargo': cargo, 'action': 'Editar'})

@login_required
@user_passes_test(is_superuser)
def cargo_delete(request, pk):
    """Eliminar cargo"""
    cargo = get_object_or_404(Cargo, pk=pk)
    if request.method == 'POST':
        cargo.delete()
        messages.success(request, 'Cargo eliminado exitosamente.')
        return redirect('cargo:list')
    return render(request, 'cargo/cargo_confirm_delete.html', {'cargo': cargo})