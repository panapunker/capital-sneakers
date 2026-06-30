from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash

from accounts.models import User
from .forms import UsuarioCrearForm, UsuarioEditarForm, UsuarioCambiarPasswordForm

es_admin = lambda u: u.is_authenticated and u.es_admin


@login_required
@user_passes_test(es_admin)
def usuario_lista(request):
    query = request.GET.get('q', '')
    rol = request.GET.get('rol', '')
    estado = request.GET.get('estado', '')

    usuarios = User.objects.all()

    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    if rol:
        usuarios = usuarios.filter(rol=rol)

    if estado == '1':
        usuarios = usuarios.filter(activo=True)
    elif estado == '0':
        usuarios = usuarios.filter(activo=False)

    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'usuarios/lista.html', {
        'page_obj': page_obj,
        'query': query,
        'rol': rol,
        'estado': estado,
        'roles': User.ROL_CHOICES,
    })


@login_required
@user_passes_test(es_admin)
def usuario_crear(request):
    if request.method == 'POST':
        form = UsuarioCrearForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('usuarios:usuario_lista')
    else:
        form = UsuarioCrearForm()

    return render(request, 'usuarios/form.html', {
        'form': form,
        'titulo': 'Nuevo Usuario',
        'accion': 'Crear Usuario',
        'es_creacion': True,
    })


@login_required
@user_passes_test(es_admin)
def usuario_detalle(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    return render(request, 'usuarios/detalle.html', {'usuario': usuario})


@login_required
@user_passes_test(es_admin)
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UsuarioEditarForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuarios:usuario_detalle', pk=usuario.pk)
    else:
        form = UsuarioEditarForm(instance=usuario)

    return render(request, 'usuarios/form.html', {
        'form': form,
        'titulo': f'Editar — {usuario.username}',
        'accion': 'Guardar cambios',
        'usuario': usuario,
        'es_creacion': False,
    })


@login_required
@user_passes_test(es_admin)
def usuario_activar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    usuario.activo = True
    usuario.is_active = True
    usuario.save()
    messages.success(request, f'Usuario {usuario.username} activado.')
    return redirect('usuarios:usuario_lista')


@login_required
@user_passes_test(es_admin)
def usuario_desactivar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario.pk == request.user.pk:
        messages.error(request, 'No puedes desactivar tu propio usuario.')
        return redirect('usuarios:usuario_lista')
    usuario.activo = False
    usuario.is_active = False
    usuario.save()
    messages.success(request, f'Usuario {usuario.username} desactivado.')
    return redirect('usuarios:usuario_lista')


@login_required
@user_passes_test(es_admin)
def usuario_cambiar_password(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UsuarioCambiarPasswordForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            if usuario.pk == request.user.pk:
                update_session_auth_hash(request, usuario)
            messages.success(request, f'Contraseña de {usuario.username} actualizada correctamente.')
            return redirect('usuarios:usuario_detalle', pk=usuario.pk)
    else:
        form = UsuarioCambiarPasswordForm(usuario)

    return render(request, 'usuarios/cambiar_password.html', {
        'form': form,
        'usuario': usuario,
    })