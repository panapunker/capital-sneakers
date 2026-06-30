from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse

from .models import (
    Devolucion, DetalleDevolucion, MovimientoDevolucion,
)
from .forms import (
    DevolucionForm, DetalleDevolucionFormSet, FiltroDevolucionForm,
)
from .barcode_utils import buscar_inventario_por_codigo
from pedidos.models import Pedido, DetallePedido
from inventario.models import Inventario, MovimientoInventario

es_admin = lambda u: u.is_authenticated and u.es_admin


# ── Funciones reutilizables de efectos sobre inventario ─────────────────

def aplicar_efecto_inventario(detalle, usuario):
    """
    Aplica los efectos sobre Inventario según el tipo de detalle de devolución.
    Reutilizable y llamado únicamente al aprobar una devolución.
    Registra MovimientoInventario y MovimientoDevolucion.
    No se ejecuta dos veces gracias al flag 'procesado'.
    """
    if detalle.procesado:
        return

    devolucion = detalle.devolucion

    # ── Cambio por talla ──────────────────────────────────────
    if detalle.es_cambio_talla():
        _procesar_cambio_talla(detalle, usuario)

    # ── Cambio por producto ───────────────────────────────────
    elif detalle.es_cambio_producto():
        _procesar_cambio_producto(detalle, usuario)

    # ── Devolución simple (total/parcial/defectuoso/garantía) ─
    else:
        if detalle.vuelve_a_inventario:
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
                usuario=usuario,
                observacion=f'Devolución #{devolucion.id} - Producto en buen estado',
            )
            MovimientoDevolucion.objects.create(
                devolucion=devolucion,
                detalle=detalle,
                accion='Stock incrementado',
                descripcion=f'{detalle.cantidad} unidades regresadas a inventario '
                            f'({detalle.producto.nombre} T{detalle.talla}).',
                usuario=usuario,
            )
        else:
            MovimientoInventario.objects.create(
                producto=detalle.producto,
                talla=detalle.talla,
                tipo='ajuste',
                cantidad=detalle.cantidad,
                usuario=usuario,
                observacion=f'Devolución #{devolucion.id} - Producto {detalle.get_estado_producto_display()}, '
                            f'no regresa a inventario',
            )
            MovimientoDevolucion.objects.create(
                devolucion=devolucion,
                detalle=detalle,
                accion='Producto marcado como defectuoso/dañado',
                descripcion=f'{detalle.cantidad} unidades NO regresan a inventario '
                            f'(estado: {detalle.get_estado_producto_display()}).',
                usuario=usuario,
            )

    # Marcar el detalle del pedido original como devuelto
    detalle.detalle_pedido.devuelto = True
    detalle.detalle_pedido.save(update_fields=['devuelto'])

    detalle.procesado = True
    detalle.save(update_fields=['procesado'])


def _procesar_cambio_talla(detalle, usuario):
    """
    Resta stock de la talla nueva (la que se entrega al cliente)
    y suma stock de la talla recibida (la devuelta), si aplica.
    """
    devolucion = detalle.devolucion
    producto = detalle.producto

    # Validar disponibilidad de la nueva talla
    inv_nueva, _ = Inventario.objects.get_or_create(
        producto=producto, talla=detalle.talla_nueva, defaults={'cantidad': 0}
    )
    if inv_nueva.cantidad < detalle.cantidad:
        MovimientoDevolucion.objects.create(
            devolucion=devolucion,
            detalle=detalle,
            accion='Cambio de talla no procesado',
            descripcion=f'Stock insuficiente en talla {detalle.talla_nueva} '
                        f'({inv_nueva.cantidad} disponibles).',
            usuario=usuario,
        )
        return

    # Restar stock de la talla nueva entregada
    inv_nueva.cantidad -= detalle.cantidad
    inv_nueva.save()
    MovimientoInventario.objects.create(
        producto=producto, talla=detalle.talla_nueva, tipo='salida',
        cantidad=detalle.cantidad, usuario=usuario,
        observacion=f'Devolución #{devolucion.id} - Entrega por cambio de talla',
    )

    # Sumar stock de la talla recibida (si vuelve a inventario)
    if detalle.vuelve_a_inventario:
        inv_recibida, _ = Inventario.objects.get_or_create(
            producto=producto, talla=detalle.talla, defaults={'cantidad': 0}
        )
        inv_recibida.cantidad += detalle.cantidad
        inv_recibida.save()
        MovimientoInventario.objects.create(
            producto=producto, talla=detalle.talla, tipo='entrada',
            cantidad=detalle.cantidad, usuario=usuario,
            observacion=f'Devolución #{devolucion.id} - Recepción por cambio de talla',
        )

    MovimientoDevolucion.objects.create(
        devolucion=devolucion,
        detalle=detalle,
        accion='Cambio de talla procesado',
        descripcion=f'{producto.nombre}: talla {detalle.talla} cambiada por '
                    f'talla {detalle.talla_nueva} ({detalle.cantidad} unidades).',
        usuario=usuario,
    )


def _procesar_cambio_producto(detalle, usuario):
    """
    Resta stock del producto nuevo entregado y suma stock
    del producto original recibido, si aplica.
    """
    devolucion = detalle.devolucion

    inv_nuevo, _ = Inventario.objects.get_or_create(
        producto=detalle.producto_nuevo, talla=detalle.talla, defaults={'cantidad': 0}
    )
    if inv_nuevo.cantidad < detalle.cantidad:
        MovimientoDevolucion.objects.create(
            devolucion=devolucion,
            detalle=detalle,
            accion='Cambio de producto no procesado',
            descripcion=f'Stock insuficiente de {detalle.producto_nuevo.nombre} '
                        f'talla {detalle.talla} ({inv_nuevo.cantidad} disponibles).',
            usuario=usuario,
        )
        return

    inv_nuevo.cantidad -= detalle.cantidad
    inv_nuevo.save()
    MovimientoInventario.objects.create(
        producto=detalle.producto_nuevo, talla=detalle.talla, tipo='salida',
        cantidad=detalle.cantidad, usuario=usuario,
        observacion=f'Devolución #{devolucion.id} - Entrega por cambio de producto',
    )

    if detalle.vuelve_a_inventario:
        inv_original, _ = Inventario.objects.get_or_create(
            producto=detalle.producto, talla=detalle.talla, defaults={'cantidad': 0}
        )
        inv_original.cantidad += detalle.cantidad
        inv_original.save()
        MovimientoInventario.objects.create(
            producto=detalle.producto, talla=detalle.talla, tipo='entrada',
            cantidad=detalle.cantidad, usuario=usuario,
            observacion=f'Devolución #{devolucion.id} - Recepción por cambio de producto',
        )

    MovimientoDevolucion.objects.create(
        devolucion=devolucion,
        detalle=detalle,
        accion='Cambio de producto procesado',
        descripcion=f'{detalle.producto.nombre} cambiado por '
                    f'{detalle.producto_nuevo.nombre} ({detalle.cantidad} unidades).',
        usuario=usuario,
    )


# ── Listado ───────────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def lista_devoluciones(request):
    form = FiltroDevolucionForm(request.GET or None)
    qs = Devolucion.objects.select_related('pedido', 'cliente', 'usuario')

    if form.is_valid():
        data = form.cleaned_data
        if data.get('fecha_inicio'):
            qs = qs.filter(fecha__date__gte=data['fecha_inicio'])
        if data.get('fecha_fin'):
            qs = qs.filter(fecha__date__lte=data['fecha_fin'])
        if data.get('cliente'):
            qs = qs.filter(
                Q(cliente__nombre_completo__icontains=data['cliente']) |
                Q(cliente__documento__icontains=data['cliente'])
            )
        if data.get('pedido_id'):
            qs = qs.filter(pedido_id=data['pedido_id'])
        if data.get('estado'):
            qs = qs.filter(estado=data['estado'])
        if data.get('tipo'):
            qs = qs.filter(tipo=data['tipo'])
        if data.get('buscar'):
            qs = qs.filter(
                Q(motivo__icontains=data['buscar']) |
                Q(observaciones__icontains=data['buscar'])
            )

    context = {
        'devoluciones': qs.order_by('-fecha'),
        'form': form,
    }
    return render(request, 'devoluciones/lista.html', context)


# ── Detalle ───────────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def detalle_devolucion(request, pk):
    devolucion = get_object_or_404(
        Devolucion.objects.select_related('pedido', 'cliente', 'usuario'),
        pk=pk
    )
    detalles = devolucion.detalles.select_related(
        'producto', 'producto_nuevo', 'detalle_pedido'
    )
    movimientos = devolucion.movimientos.select_related('usuario', 'detalle')

    context = {
        'devolucion': devolucion,
        'detalles': detalles,
        'movimientos': movimientos,
    }
    return render(request, 'devoluciones/detalle.html', context)


# ── Crear devolución desde un pedido ─────────────────────────────────

@login_required
@user_passes_test(es_admin)
def crear_devolucion(request, pedido_id):
    pedido = get_object_or_404(
        Pedido.objects.select_related('cliente'), pk=pedido_id
    )

    if pedido.estado == 'cancelado':
        messages.error(request, 'No se pueden crear devoluciones de pedidos cancelados.')
        return redirect('pedidos:pedido_detalle', pedido_id=pedido.id)

    detalles_disponibles = pedido.detalles.filter(devuelto=False).select_related('producto')

    if not detalles_disponibles.exists():
        messages.error(request, 'Este pedido ya fue completamente devuelto.')
        return redirect('pedidos:pedido_detalle', pedido_id=pedido.id)

    if request.method == 'POST':
        form = DevolucionForm(request.POST)
        detalle_ids = request.POST.getlist('detalle_pedido_id')

        if not detalle_ids:
            messages.error(request, 'Debes seleccionar al menos un producto para devolver.')
        elif form.is_valid():
            with transaction.atomic():
                devolucion = form.save(commit=False)
                devolucion.pedido = pedido
                devolucion.cliente = pedido.cliente
                devolucion.usuario = request.user
                devolucion.save()

                for det_id in detalle_ids:
                    detalle_pedido = get_object_or_404(DetallePedido, pk=det_id, pedido=pedido)
                    cantidad = int(request.POST.get(f'cantidad_{det_id}', detalle_pedido.cantidad))
                    talla_nueva = request.POST.get(f'talla_nueva_{det_id}', '') or None
                    producto_nuevo_id = request.POST.get(f'producto_nuevo_{det_id}', '') or None
                    estado_producto = request.POST.get(f'estado_producto_{det_id}', 'nuevo')
                    motivo_linea = request.POST.get(f'motivo_{det_id}', '')

                    DetalleDevolucion.objects.create(
                        devolucion=devolucion,
                        detalle_pedido=detalle_pedido,
                        producto=detalle_pedido.producto,
                        talla=detalle_pedido.talla,
                        cantidad=cantidad,
                        motivo=motivo_linea,
                        estado_producto=estado_producto,
                        vuelve_a_inventario=estado_producto in ('nuevo', 'usado'),
                        talla_nueva=talla_nueva,
                        producto_nuevo_id=producto_nuevo_id,
                    )

                MovimientoDevolucion.objects.create(
                    devolucion=devolucion,
                    accion='Devolución creada',
                    descripcion=f'Devolución registrada para el pedido #{pedido.id}.',
                    usuario=request.user,
                )

            messages.success(request, f'Devolución #{devolucion.id} creada correctamente.')
            return redirect('devoluciones:detalle', pk=devolucion.id)
    else:
        form = DevolucionForm()

    from inventario.models import TALLAS_CHOICES

    context = {
        'pedido': pedido,
        'detalles_disponibles': detalles_disponibles,
        'form': form,
        'tallas_choices': TALLAS_CHOICES,
    }
    return render(request, 'devoluciones/crear.html', context)


# ── Acciones sobre estado ─────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def aprobar_devolucion(request, pk):
    devolucion = get_object_or_404(Devolucion, pk=pk)

    if not devolucion.puede_aprobarse():
        messages.error(request, 'Solo se pueden aprobar devoluciones pendientes.')
        return redirect('devoluciones:detalle', pk=pk)

    with transaction.atomic():
        for detalle in devolucion.detalles.select_related('detalle_pedido', 'producto'):
            aplicar_efecto_inventario(detalle, request.user)

        devolucion.estado = 'aprobada'
        devolucion.save(update_fields=['estado', 'fecha_actualizacion'])

        MovimientoDevolucion.objects.create(
            devolucion=devolucion,
            accion='Devolución aprobada',
            descripcion='La devolución fue aprobada y se aplicaron los efectos sobre inventario.',
            usuario=request.user,
        )

        # Preparado para Notificaciones (no se implementa aún la llamada real)
        # from notificaciones.models import Notificacion
        # Notificacion.crear(tipo=..., titulo=..., usuario=request.user)

    messages.success(request, f'Devolución #{devolucion.id} aprobada correctamente.')
    return redirect('devoluciones:detalle', pk=pk)


@login_required
@user_passes_test(es_admin)
def rechazar_devolucion(request, pk):
    devolucion = get_object_or_404(Devolucion, pk=pk)

    if not devolucion.puede_rechazarse():
        messages.error(request, 'Solo se pueden rechazar devoluciones pendientes.')
        return redirect('devoluciones:detalle', pk=pk)

    devolucion.estado = 'rechazada'
    devolucion.save(update_fields=['estado', 'fecha_actualizacion'])

    MovimientoDevolucion.objects.create(
        devolucion=devolucion,
        accion='Devolución rechazada',
        descripcion=request.POST.get('motivo_rechazo', 'Sin motivo especificado.'),
        usuario=request.user,
    )

    messages.success(request, f'Devolución #{devolucion.id} rechazada.')
    return redirect('devoluciones:detalle', pk=pk)


@login_required
@user_passes_test(es_admin)
def finalizar_devolucion(request, pk):
    devolucion = get_object_or_404(Devolucion, pk=pk)

    if not devolucion.puede_finalizarse():
        messages.error(request, 'Solo se pueden finalizar devoluciones aprobadas.')
        return redirect('devoluciones:detalle', pk=pk)

    devolucion.estado = 'finalizada'
    devolucion.save(update_fields=['estado', 'fecha_actualizacion'])

    MovimientoDevolucion.objects.create(
        devolucion=devolucion,
        accion='Devolución finalizada',
        descripcion='El proceso de devolución ha sido cerrado.',
        usuario=request.user,
    )

    messages.success(request, f'Devolución #{devolucion.id} finalizada.')
    return redirect('devoluciones:detalle', pk=pk)


@login_required
@user_passes_test(es_admin)
def imprimir_devolucion(request, pk):
    devolucion = get_object_or_404(
        Devolucion.objects.select_related('pedido', 'cliente', 'usuario'), pk=pk
    )
    detalles = devolucion.detalles.select_related('producto', 'producto_nuevo')

    context = {
        'devolucion': devolucion,
        'detalles': detalles,
    }
    return render(request, 'devoluciones/imprimir.html', context)


# ── API preparada para lector de código de barras ────────────────────

@login_required
@user_passes_test(es_admin)
def api_buscar_codigo_barras(request):
    """
    Endpoint preparado para el lector USB.
    Recibe un código escaneado y retorna el producto/talla asociado.
    No implementa todavía la captura en tiempo real en el frontend.
    """
    codigo = request.GET.get('codigo', '')
    inventario = buscar_inventario_por_codigo(codigo)

    if not inventario:
        return JsonResponse({'encontrado': False})

    return JsonResponse({
        'encontrado': True,
        'producto_id': inventario.producto_id,
        'producto_nombre': inventario.producto.nombre,
        'talla': inventario.talla,
        'cantidad_disponible': inventario.cantidad,
    })