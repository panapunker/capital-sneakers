from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.paginator import Paginator

from catalogo.models import Producto
from .models import Inventario, MovimientoInventario, TALLAS_CHOICES
from .forms import AjusteInventarioForm


@login_required
def inventario_lista(request):
    query = request.GET.get('q', '')
    productos = Producto.objects.all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(referencia__icontains=query) |
            Q(marca__nombre__icontains=query)
        )

    productos_data = []
    for producto in productos:
        total = Inventario.objects.filter(producto=producto).aggregate(
            total=Sum('cantidad')
        )['total'] or 0
        productos_data.append({
            'producto': producto,
            'total': total,
        })

    paginator = Paginator(productos_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventario/lista.html', {
        'page_obj': page_obj,
        'query': query,
    })


@login_required
def inventario_detalle(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    inventarios = Inventario.objects.filter(producto=producto)
    total = inventarios.aggregate(total=Sum('cantidad'))['total'] or 0

    return render(request, 'inventario/detalle.html', {
        'producto': producto,
        'inventarios': inventarios,
        'total': total,
    })


@login_required
def inventario_ajustar(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    inventarios = Inventario.objects.filter(producto=producto)

    if request.method == 'POST':
        form = AjusteInventarioForm(request.POST)
        if form.is_valid():
            talla = form.cleaned_data['talla']
            tipo = form.cleaned_data['tipo']
            cantidad = form.cleaned_data['cantidad']
            observacion = form.cleaned_data['observacion']

            inv, _ = Inventario.objects.get_or_create(
                producto=producto,
                talla=talla,
                defaults={'cantidad': 0}
            )

            if tipo == 'entrada':
                inv.cantidad += cantidad
            elif tipo == 'salida':
                if inv.cantidad - cantidad < 0:
                    messages.error(request, 'No hay suficiente stock para realizar la salida.')
                    return redirect('inventario:ajustar', producto_id=producto_id)
                inv.cantidad -= cantidad
            elif tipo == 'ajuste':
                inv.cantidad = cantidad

            inv.save()

            MovimientoInventario.objects.create(
                producto=producto,
                talla=talla,
                tipo=tipo,
                cantidad=cantidad,
                usuario=request.user,
                observacion=observacion,
            )

            messages.success(request, 'Inventario actualizado correctamente.')
            return redirect('inventario:detalle', producto_id=producto_id)
    else:
        form = AjusteInventarioForm()

    return render(request, 'inventario/ajustar.html', {
        'producto': producto,
        'inventarios': inventarios,
        'form': form,
        'tallas_choices': TALLAS_CHOICES,
    })


@login_required
def movimientos_lista(request):
    movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').all()

    q_producto = request.GET.get('producto', '')
    q_tipo = request.GET.get('tipo', '')
    q_usuario = request.GET.get('usuario', '')
    q_fecha_desde = request.GET.get('fecha_desde', '')
    q_fecha_hasta = request.GET.get('fecha_hasta', '')

    if q_producto:
        movimientos = movimientos.filter(
            Q(producto__nombre__icontains=q_producto) |
            Q(producto__referencia__icontains=q_producto)
        )
    if q_tipo:
        movimientos = movimientos.filter(tipo=q_tipo)
    if q_usuario:
        movimientos = movimientos.filter(
            Q(usuario__username__icontains=q_usuario) |
            Q(usuario__first_name__icontains=q_usuario)
        )
    if q_fecha_desde:
        movimientos = movimientos.filter(fecha__date__gte=q_fecha_desde)
    if q_fecha_hasta:
        movimientos = movimientos.filter(fecha__date__lte=q_fecha_hasta)

    paginator = Paginator(movimientos, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventario/movimientos.html', {
        'page_obj': page_obj,
        'q_producto': q_producto,
        'q_tipo': q_tipo,
        'q_usuario': q_usuario,
        'q_fecha_desde': q_fecha_desde,
        'q_fecha_hasta': q_fecha_hasta,
        'tipos': MovimientoInventario._meta.get_field('tipo').choices,
    })