from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Pedido, DetallePedido
from .forms import PedidoForm, DetallePedidoForm, PedidoEstadoForm
from inventario.models import Inventario, MovimientoInventario
from catalogo.models import Producto
from notificaciones.utils import notif_nuevo_pedido, notif_stock_bajo, notif_producto_agotado


@login_required
def pedido_lista(request):
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')

    pedidos = Pedido.objects.select_related('cliente', 'usuario').all()

    if query:
        pedidos = pedidos.filter(
            Q(cliente__nombre_completo__icontains=query) |
            Q(cliente__documento__icontains=query) |
            Q(id__icontains=query)
        )

    if estado:
        pedidos = pedidos.filter(estado=estado)

    paginator = Paginator(pedidos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pedidos/lista.html', {
        'page_obj': page_obj,
        'query': query,
        'estado': estado,
        'estados': Pedido._meta.get_field('estado').choices,
    })


@login_required
def pedido_crear(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.usuario = request.user
            pedido.save()
            notif_nuevo_pedido(pedido)
            messages.success(request, 'Pedido creado. Ahora agrega los productos.')
            return redirect('pedidos:pedido_agregar_detalle', pedido_id=pedido.id)
    else:
        form = PedidoForm()

    return render(request, 'pedidos/form.html', {
        'form': form,
        'titulo': 'Nuevo Pedido',
        'accion': 'Crear Pedido',
    })


@login_required
def pedido_detalle(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    detalles = pedido.detalles.select_related('producto').all()

    return render(request, 'pedidos/detalle.html', {
        'pedido': pedido,
        'detalles': detalles,
    })


@login_required
def pedido_agregar_detalle(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    detalles = pedido.detalles.select_related('producto').all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        talla = request.POST.get('talla')
        cantidad = int(request.POST.get('cantidad', 0))

        try:
            producto = Producto.objects.get(pk=producto_id)
            inv = Inventario.objects.get(producto=producto, talla=talla)

            if cantidad <= 0:
                messages.error(request, 'La cantidad debe ser mayor a cero.')
            elif inv.cantidad < cantidad:
                messages.error(request, f'Stock insuficiente. Disponible: {inv.cantidad} unidades.')
            else:
                inv.cantidad -= cantidad
                inv.save()

                if inv.cantidad == 0:
                    notif_producto_agotado(producto)
                elif inv.cantidad <= 5:
                    notif_stock_bajo(producto, inv.cantidad)

                MovimientoInventario.objects.create(
                    producto=producto,
                    talla=talla,
                    tipo='salida',
                    cantidad=cantidad,
                    usuario=request.user,
                    observacion=f'Salida por Pedido #{pedido.id}',
                )

                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    talla=talla,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta,
                    subtotal=producto.precio_venta * cantidad,
                )

                pedido.calcular_total()
                messages.success(request, 'Producto agregado correctamente.')

        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')
        except Inventario.DoesNotExist:
            messages.error(request, 'No existe inventario para esa talla.')

        return redirect('pedidos:pedido_agregar_detalle', pedido_id=pedido.id)

    form = DetallePedidoForm()

    return render(request, 'pedidos/agregar_detalle.html', {
        'pedido': pedido,
        'detalles': detalles,
        'form': form,
    })


@login_required
def pedido_eliminar_detalle(request, detalle_id):
    detalle = get_object_or_404(DetallePedido, pk=detalle_id)
    pedido = detalle.pedido

    inv, _ = Inventario.objects.get_or_create(
        producto=detalle.producto,
        talla=detalle.talla,
        defaults={'cantidad': 0}
    )
    inv.cantidad += detalle.cantidad
    inv.save()

    MovimientoInventario.objects.create(
        producto=detalle.producto,
        talla=detalle.talla,
        tipo='entrada',
        cantidad=detalle.cantidad,
        usuario=request.user,
        observacion=f'Devolución por eliminación de detalle en Pedido #{pedido.id}',
    )

    detalle.delete()
    pedido.calcular_total()
    messages.success(request, 'Producto eliminado del pedido.')
    return redirect('pedidos:pedido_agregar_detalle', pedido_id=pedido.id)


@login_required
def pedido_estado(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    if request.method == 'POST':
        form = PedidoEstadoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estado actualizado correctamente.')
            return redirect('pedidos:pedido_detalle', pedido_id=pedido.id)
    else:
        form = PedidoEstadoForm(instance=pedido)

    return render(request, 'pedidos/estado.html', {
        'pedido': pedido,
        'form': form,
    })
# ── Vistas cliente ────────────────────────────────────────────────────────────

@login_required
def mis_pedidos(request):
    try:
        cliente = request.user.cliente
    except Exception:
        messages.error(request, 'No tienes perfil de cliente.')
        return redirect('dashboard:cliente_dashboard')

    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha')
    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})


@login_required
def mi_pedido_detalle(request, pedido_id):
    try:
        cliente = request.user.cliente
    except Exception:
        return redirect('dashboard:cliente_dashboard')

    pedido   = get_object_or_404(Pedido, id=pedido_id, cliente=cliente)
    detalles = pedido.detalles.select_related('producto', 'producto__marca')
    return render(request, 'pedidos/mi_pedido_detalle.html', {
        'pedido':   pedido,
        'detalles': detalles,
    })
# ── Facturar pedido ────────────────────────────────────────────────────────────

@login_required
def facturar_pedido(request, pedido_id):
    if request.method != 'POST':
        return redirect('pedidos:pedido_detalle', pedido_id=pedido_id)

    pedido = get_object_or_404(Pedido, pk=pedido_id)

    if pedido.facturado:
        messages.warning(request, f'El pedido #{pedido.id} ya fue facturado.')
        return redirect('pedidos:pedido_detalle', pedido_id=pedido_id)

    from django.utils import timezone
    pedido.facturado = True
    pedido.fecha_factura = timezone.now()
    pedido.estado = 'entregado'
    pedido.save()

    messages.success(
        request,
        f'Pedido #{pedido.id} facturado. '
        f'<a href="/pedidos/{pedido.id}/factura-pdf/" class="alert-link">'
        f'Descargar factura PDF</a>'
    )
    return redirect('pedidos:factura_pdf', pedido_id=pedido_id)


@login_required
def factura_pdf(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    detalles = pedido.detalles.select_related('producto', 'producto__marca').all()

    from django.http import HttpResponse
    from django.template.loader import render_to_string
    import io

    # Genera HTML de la factura
    html = render_to_string('pedidos/factura_pdf.html', {
        'pedido': pedido,
        'detalles': detalles,
    }, request=request)

    # Intenta generar PDF con weasyprint si está instalado
    try:
        from weasyprint import HTML as WeasyHTML
        pdf_file = io.BytesIO()
        WeasyHTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(pdf_file)
        pdf_file.seek(0)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{pedido.id}.pdf"'
        return response
    except ImportError:
        # Si no hay weasyprint, devuelve HTML imprimible
        return HttpResponse(html)
    return redirect('pedidos:pedido_detalle', pedido_id=pedido_id)


# ── Devolver pedido ────────────────────────────────────────────────────────────

@login_required
@transaction.atomic
def devolver_pedido(request, pedido_id):
    if request.method != 'POST':
        return redirect('pedidos:pedido_detalle', pedido_id=pedido_id)

    pedido = get_object_or_404(Pedido, pk=pedido_id)

    if pedido.estado == 'cancelado':
        messages.warning(request, f'El pedido #{pedido.id} ya fue cancelado.')
        return redirect('pedidos:pedido_detalle', pedido_id=pedido_id)

    detalles = pedido.detalles.filter(devuelto=False).select_related('producto')

    if not detalles.exists():
        messages.warning(request, f'El pedido #{pedido.id} no tiene productos por devolver.')
        return redirect('pedidos:pedido_detalle', pedido_id=pedido_id)

    for detalle in detalles:
        # Devuelve stock al inventario
        inv, _ = Inventario.objects.get_or_create(
            producto=detalle.producto,
            talla=detalle.talla,
            defaults={'cantidad': 0}
        )
        inv.cantidad += detalle.cantidad
        inv.save()

        # Devuelve stock a StockTalla
        from catalogo.models import StockTalla
        st, _ = StockTalla.objects.get_or_create(
            producto=detalle.producto,
            talla=detalle.talla,
            defaults={'cantidad': 0}
        )
        st.cantidad += detalle.cantidad
        st.save()

        # Registra movimiento de entrada
        MovimientoInventario.objects.create(
            producto=detalle.producto,
            talla=detalle.talla,
            tipo='entrada',
            cantidad=detalle.cantidad,
            usuario=request.user,
            observacion=f'Devolución Pedido #{pedido.id}',
        )

        # Marca el detalle como devuelto
        detalle.devuelto = True
        detalle.save()

    # Marca pedido como cancelado y no facturado
    # para que el balance desaparezca automáticamente
    pedido.estado = 'cancelado'
    pedido.facturado = True  # Lo saca del balance
    pedido.save()

    messages.success(
        request,
        f'Devolución del pedido #{pedido.id} procesada. '
        f'Stock restaurado y balance actualizado.'
    )
    return redirect('pedidos:pedido_detalle', pedido_id=pedido_id)