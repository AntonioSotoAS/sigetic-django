from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Categoria, Subcategoria
from .forms import CategoriaForm, SubcategoriaForm

def is_superuser(user):
    return user.is_superuser

# Vista para Categorías
@login_required
@user_passes_test(is_superuser)
def categoria_list(request):
    """Lista todas las categorías"""
    categorias = Categoria.objects.all()
    return render(request, 'categoria/categoria_list.html', {'categorias': categorias})

@login_required
@user_passes_test(is_superuser)
def categoria_create(request):
    """Crear nueva categoría"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('categoria:list')
    else:
        form = CategoriaForm()
    return render(request, 'categoria/categoria_form.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(is_superuser)
def categoria_edit(request, pk):
    """Editar categoría existente"""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('categoria:list')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'categoria/categoria_form.html', {'form': form, 'categoria': categoria, 'action': 'Editar'})

@login_required
@user_passes_test(is_superuser)
def categoria_delete(request, pk):
    """Eliminar categoría"""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
        return redirect('categoria:list')
    return render(request, 'categoria/categoria_confirm_delete.html', {'categoria': categoria})

# Vista para Subcategorías
@login_required
@user_passes_test(is_superuser)
def subcategoria_list(request):
    """Lista todas las subcategorías"""
    subcategorias = Subcategoria.objects.all()
    return render(request, 'categoria/subcategoria_list.html', {'subcategorias': subcategorias})

@login_required
@user_passes_test(is_superuser)
def subcategoria_create(request):
    """Crear nueva subcategoría"""
    if request.method == 'POST':
        form = SubcategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategoría creada exitosamente.')
            return redirect('categoria:subcategoria_list')
    else:
        form = SubcategoriaForm()
    return render(request, 'categoria/subcategoria_form.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(is_superuser)
def subcategoria_edit(request, pk):
    """Editar subcategoría existente"""
    subcategoria = get_object_or_404(Subcategoria, pk=pk)
    if request.method == 'POST':
        form = SubcategoriaForm(request.POST, instance=subcategoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategoría actualizada exitosamente.')
            return redirect('categoria:subcategoria_list')
    else:
        form = SubcategoriaForm(instance=subcategoria)
    return render(request, 'categoria/subcategoria_form.html', {'form': form, 'subcategoria': subcategoria, 'action': 'Editar'})

@login_required
@user_passes_test(is_superuser)
def subcategoria_delete(request, pk):
    """Eliminar subcategoría"""
    subcategoria = get_object_or_404(Subcategoria, pk=pk)
    if request.method == 'POST':
        subcategoria.delete()
        messages.success(request, 'Subcategoría eliminada exitosamente.')
        return redirect('categoria:subcategoria_list')
    return render(request, 'categoria/subcategoria_confirm_delete.html', {'subcategoria': subcategoria})
