from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Proveedor, Compra, DetalleCompra
from .forms import ProveedorForm, CompraForm, DetalleCompraForm
from inventario.models import Inventario, MovimientoInventario
from catalogo.models import Producto
from notificaciones.utils import notif_compra_recibida, notif_compra_cancelada

es_admin = lambda u: u.is_authenticated and u.es_admin


# ==================== PROVEEDORES ====================

@login_required
@user_passes_test(es_admin)
def proveedor_lista(request):
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')

    proveedores = Proveedor.objects.all()

    if query:
        proveedores = proveedores.filter(
            Q(empresa__icontains=query) |
            Q(nit__icontains=query) |
            Q(contacto__icontains=query)
        )
    if estado:
        proveedores = proveedores.filter(estado=estado)

    return render(request, 'compras/proveedores/lista.html', {
        'proveedores': proveedores,
        'query': query,
        'estado': estado,
    })


@login_required
@user_passes_test(es_admin)
def proveedor_crear(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado correctamente.')
            return redirect('compras:proveedor_lista')
    else:
        form = ProveedorForm()
    return render(request, 'compras/proveedores/form.html', {'form': form, 'titulo': 'Nuevo Proveedor'})


@login_required
@user_passes_test(es_admin)
def proveedor_editar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado correctamente.')
            return redirect('compras:proveedor_lista')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'compras/proveedores/form.html', {'form': form, 'titulo': 'Editar Proveedor'})


@login_required
@user_passes_test(es_admin)
def proveedor_eliminar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado correctamente.')
        return redirect('compras:proveedor_lista')
    return render(request, 'compras/proveedores/confirmar_eliminar.html', {'objeto': proveedor})


# ==================== COMPRAS ====================

@login_required
@user_passes_test(es_admin)
def compra_lista(request):
    proveedor_id = request.GET.get('proveedor', '')
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    numero = request.GET.get('numero', '')

    compras = Compra.objects.select_related('proveedor', 'usuario_creo').all()

    if proveedor_id:
        compras = compras.filter(proveedor__id=proveedor_id)
    if estado:
        compras = compras.filter(estado=estado)
    if fecha_inicio:
        compras = compras.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        compras = compras.filter(fecha__date__lte=fecha_fin)
    if numero:
        compras = compras.filter(id__icontains=numero)

    paginator = Paginator(compras, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'compras/compras/lista.html', {
        'page_obj': page_obj,
        'proveedores': Proveedor.objects.filter(estado='activo'),
        'proveedor_sel': proveedor_id,
        'estado_sel': estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'numero': numero,
    })


@login_required
@user_passes_test(es_admin)
def compra_crear(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save(commit=False)
            compra.usuario_creo = request.user
            compra.save()
            messages.success(request, 'Compra creada. Ahora agrega los productos.')
            return redirect('compras:compra_agregar_detalle', pk=compra.pk)
    else:
        form = CompraForm()
    return render(request, 'compras/compras/form.html', {'form': form, 'titulo': 'Nueva Compra'})


@login_required
@user_passes_test(es_admin)
def compra_detalle(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    detalles = compra.detalles.select_related('producto').all()
    return render(request, 'compras/compras/detalle.html', {
        'compra': compra,
        'detalles': detalles,
        'total': compra.calcular_total(),
    })


@login_required
@user_passes_test(es_admin)
def compra_agregar_detalle(request, pk):
    compra = get_object_or_404(Compra, pk=pk)

    if compra.estado != 'pendiente':
        messages.warning(request, 'Solo se pueden agregar productos a compras pendientes.')
        return redirect('compras:compra_detalle', pk=pk)

    detalles = compra.detalles.select_related('producto').all()

    if request.method == 'POST':
        form = DetalleCompraForm(request.POST)
        if form.is_valid():
            DetalleCompra.objects.create(
                compra=compra,
                producto=form.cleaned_data['producto'],
                talla=form.cleaned_data['talla'],
                cantidad=form.cleaned_data['cantidad'],
                costo_unitario=form.cleaned_data['costo_unitario'],
                subtotal=form.cleaned_data['cantidad'] * form.cleaned_data['costo_unitario'],
            )
            messages.success(request, 'Producto agregado a la compra.')
            return redirect('compras:compra_agregar_detalle', pk=pk)
    else:
        form = DetalleCompraForm()

    return render(request, 'compras/compras/agregar_detalle.html', {
        'compra': compra,
        'detalles': detalles,
        'form': form,
        'total': compra.calcular_total(),
    })


@login_required
@user_passes_test(es_admin)
def compra_eliminar_detalle(request, detalle_id):
    detalle = get_object_or_404(DetalleCompra, pk=detalle_id)
    compra = detalle.compra

    if compra.estado != 'pendiente':
        messages.warning(request, 'No se puede modificar una compra ya procesada.')
        return redirect('compras:compra_detalle', pk=compra.pk)

    detalle.delete()
    messages.success(request, 'Producto eliminado de la compra.')
    return redirect('compras:compra_agregar_detalle', pk=compra.pk)


@login_required
@user_passes_test(es_admin)
@transaction.atomic
def compra_confirmar_recepcion(request, pk):
    compra = get_object_or_404(Compra, pk=pk)

    if request.method != 'POST':
        return redirect('compras:compra_detalle', pk=pk)

    if compra.estado == 'recibida':
        messages.warning(request, 'Esta compra ya fue recibida.')
        return redirect('compras:compra_detalle', pk=pk)

    if compra.estado == 'cancelada':
        messages.error(request, 'No se puede recibir una compra cancelada.')
        return redirect('compras:compra_detalle', pk=pk)

    detalles = compra.detalles.select_related('producto').all()

    if not detalles.exists():
        messages.error(request, 'La compra no tiene productos.')
        return redirect('compras:compra_detalle', pk=pk)

    for detalle in detalles:
        # Aumenta Inventario
        inv, _ = Inventario.objects.get_or_create(
            producto=detalle.producto,
            talla=detalle.talla,
            defaults={'cantidad': 0}
        )
        inv.cantidad += detalle.cantidad
        inv.save()

        # Sincroniza StockTalla en catálogo
        from catalogo.models import StockTalla
        st, _ = StockTalla.objects.get_or_create(
            producto=detalle.producto,
            talla=detalle.talla,
            defaults={'cantidad': 0}
        )
        st.cantidad += detalle.cantidad
        st.save()

        # Crea movimiento de inventario
        MovimientoInventario.objects.create(
            producto=detalle.producto,
            talla=detalle.talla,
            tipo='entrada',
            cantidad=detalle.cantidad,
            usuario=request.user,
            observacion=f'Compra #{compra.id} recibida - {compra.proveedor.empresa}',
        )

        # NOTA: arquitectura preparada para costo promedio ponderado.
        # Pendiente implementar cálculo definitivo. No tocar hasta entonces.
        # detalle.producto.precio_compra = calcular_costo_promedio(detalle.producto, detalle.costo_unitario, detalle.cantidad)
        # detalle.producto.save()

    compra.estado = 'recibida'
    compra.usuario_confirmo = request.user
    compra.fecha_recibida = timezone.now()
    compra.save()

    notif_compra_recibida(compra)

    messages.success(request, f'Compra #{compra.id} recibida. Inventario actualizado correctamente.')
    return redirect('compras:compra_detalle', pk=pk)


@login_required
@user_passes_test(es_admin)
def compra_cancelar(request, pk):
    compra = get_object_or_404(Compra, pk=pk)

    if request.method != 'POST':
        return redirect('compras:compra_detalle', pk=pk)

    if compra.estado == 'recibida':
        messages.error(request, 'No se puede cancelar una compra ya recibida.')
        return redirect('compras:compra_detalle', pk=pk)

    compra.estado = 'cancelada'
    compra.save()

    notif_compra_cancelada(compra)

    messages.success(request, f'Compra #{compra.id} cancelada.')
    return redirect('compras:compra_detalle', pk=pk)


# ==================== REPORTES DE COMPRAS ====================

@login_required
@user_passes_test(es_admin)
def reporte_compras(request):
    compras_recibidas = Compra.objects.filter(estado='recibida')

    total_comprado = sum(c.calcular_total() for c in compras_recibidas)
    cantidad_compras = compras_recibidas.count()

    proveedor_top = (
        DetalleCompra.objects
        .filter(compra__estado='recibida')
        .values('compra__proveedor__empresa')
        .annotate(total_compras=Count('compra', distinct=True))
        .order_by('-total_compras')
        .first()
    )

    productos_mas_comprados = (
        DetalleCompra.objects
        .filter(compra__estado='recibida')
        .values('producto__nombre')
        .annotate(total_unidades=Sum('cantidad'))
        .order_by('-total_unidades')[:10]
    )

    grafica_productos = {
        'labels': [p['producto__nombre'] for p in productos_mas_comprados],
        'data': [p['total_unidades'] for p in productos_mas_comprados],
    }

    return render(request, 'compras/reportes.html', {
        'total_comprado': total_comprado,
        'cantidad_compras': cantidad_compras,
        'proveedor_top': proveedor_top,
        'productos_mas_comprados': productos_mas_comprados,
        'grafica_productos': grafica_productos,
    })