from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Cliente
from .forms import ClienteCrearForm, ClienteEditarForm
from notificaciones.utils import notif_nuevo_cliente


@login_required
def cliente_lista(request):
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')

    clientes = Cliente.objects.all()

    if query:
        clientes = clientes.filter(
            Q(nombre_completo__icontains=query) |
            Q(documento__icontains=query) |
            Q(telefono__icontains=query) |
            Q(correo__icontains=query) |
            Q(ciudad__icontains=query)
        )

    if estado:
        clientes = clientes.filter(estado=estado)

    paginator = Paginator(clientes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'clientes/lista.html', {
        'page_obj': page_obj,
        'query': query,
        'estado': estado,
    })


@login_required
def cliente_crear(request):
    if request.method == 'POST':
        form = ClienteCrearForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            notif_nuevo_cliente(cliente)
            messages.success(request, 'Cliente creado correctamente.')
            return redirect('clientes:cliente_lista')
    else:
        form = ClienteCrearForm()

    return render(request, 'clientes/form.html', {
        'form': form,
        'titulo': 'Nuevo Cliente',
        'accion': 'Crear',
    })


@login_required
def cliente_detalle(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
    })


@login_required
def cliente_editar(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    if request.method == 'POST':
        form = ClienteEditarForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('clientes:cliente_detalle', cliente_id=cliente.id)
    else:
        form = ClienteEditarForm(instance=cliente)

    return render(request, 'clientes/form.html', {
        'form': form,
        'titulo': f'Editar — {cliente.nombre_completo}',
        'accion': 'Guardar cambios',
        'cliente': cliente,
    })
# ── Vista perfil para cliente ─────────────────────────────────────────────────

@login_required
def mi_perfil(request):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes perfil de cliente.')
        return redirect('dashboard:cliente_dashboard')

    pedidos_pendientes = cliente.pedidos.filter(
        facturado=False
    ).order_by('-fecha')

    return render(request, 'clientes/mi_perfil.html', {
        'cliente': cliente,
        'pedidos_pendientes': pedidos_pendientes,
    })