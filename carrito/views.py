from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Carrito, ItemCarrito
from catalogo.models import Producto
from inventario.models import Inventario, MovimientoInventario
from pedidos.models import Pedido, DetallePedido
from clientes.models import Cliente
from notificaciones.utils import notif_nuevo_pedido, notif_stock_bajo, notif_producto_agotado


def get_or_create_carrito(usuario):
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    return carrito


def verificar_stock(producto, talla, cantidad):
    try:
        inv = Inventario.objects.get(producto=producto, talla=talla)
        return inv.cantidad >= cantidad, inv.cantidad
    except Inventario.DoesNotExist:
        return False, 0


@login_required
def ver_carrito(request):
    carrito = get_or_create_carrito(request.user)
    items = carrito.items.select_related('producto', 'producto__marca').all()

    items_con_stock = []
    for item in items:
        stock = item.get_stock_disponible()
        items_con_stock.append({
            'item': item,
            'stock': stock,
            'subtotal': item.get_subtotal(),
        })

    context = {
        'carrito': carrito,
        'items_con_stock': items_con_stock,
        'total': carrito.get_total(),
        'total_items': carrito.get_total_items(),
    }
    return render(request, 'carrito/carrito.html', context)


@login_required
def agregar_item(request):
    if request.method != 'POST':
        return redirect('carrito:ver_carrito')

    producto_id = request.POST.get('producto_id')
    talla = request.POST.get('talla')
    cantidad = request.POST.get('cantidad', 1)

    producto = get_object_or_404(Producto, id=producto_id, activo=True)

    if not talla:
        messages.error(request, 'Debes seleccionar una talla.')
        return redirect(request.META.get('HTTP_REFERER', 'carrito:ver_carrito'))

    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, 'La cantidad debe ser un número positivo.')
        return redirect(request.META.get('HTTP_REFERER', 'carrito:ver_carrito'))

    disponible, stock_actual = verificar_stock(producto, talla, cantidad)
    if not disponible:
        if stock_actual == 0:
            messages.error(request, f'No hay stock disponible para {producto.nombre} talla {talla}.')
        else:
            messages.error(request, f'Solo hay {stock_actual} unidades disponibles de {producto.nombre} talla {talla}.')
        return redirect(request.META.get('HTTP_REFERER', 'carrito:ver_carrito'))

    carrito = get_or_create_carrito(request.user)

    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        talla=talla,
        defaults={
            'cantidad': cantidad,
            'precio_unitario': producto.precio_venta,
        }
    )

    if not creado:
        nueva_cantidad = item.cantidad + cantidad
        disponible, stock_actual = verificar_stock(producto, talla, nueva_cantidad)
        if not disponible:
            messages.error(request, f'No puedes agregar más. Solo hay {stock_actual} unidades disponibles.')
            return redirect(request.META.get('HTTP_REFERER', 'carrito:ver_carrito'))
        item.cantidad = nueva_cantidad
        item.precio_unitario = producto.precio_venta
        item.save()
        messages.success(request, f'Se actualizó la cantidad de {producto.nombre} talla {talla}.')
    else:
        messages.success(request, f'{producto.nombre} talla {talla} agregado al carrito.')

    return redirect('carrito:ver_carrito')


@login_required
def eliminar_item(request, item_id):
    carrito = get_or_create_carrito(request.user)
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
    nombre = f'{item.producto.nombre} talla {item.talla}'
    item.delete()
    messages.success(request, f'{nombre} eliminado del carrito.')
    return redirect('carrito:ver_carrito')


@login_required
def actualizar_cantidad(request, item_id):
    if request.method != 'POST':
        return redirect('carrito:ver_carrito')

    carrito = get_or_create_carrito(request.user)
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)

    accion = request.POST.get('accion')

    if accion == 'incrementar':
        nueva_cantidad = item.cantidad + 1
        disponible, stock_actual = verificar_stock(item.producto, item.talla, nueva_cantidad)
        if not disponible:
            messages.error(request, f'Solo hay {stock_actual} unidades disponibles.')
            return redirect('carrito:ver_carrito')
        item.cantidad = nueva_cantidad
        item.save()

    elif accion == 'decrementar':
        if item.cantidad <= 1:
            nombre = f'{item.producto.nombre} talla {item.talla}'
            item.delete()
            messages.success(request, f'{nombre} eliminado del carrito.')
            return redirect('carrito:ver_carrito')
        item.cantidad -= 1
        item.save()

    return redirect('carrito:ver_carrito')


@login_required
def vaciar_carrito(request):
    if request.method == 'POST':
        carrito = get_or_create_carrito(request.user)
        carrito.vaciar()
        messages.success(request, 'El carrito ha sido vaciado.')
    return redirect('carrito:ver_carrito')


@login_required
@transaction.atomic
def confirmar_carrito(request):
    if request.method != 'POST':
        return redirect('carrito:ver_carrito')

    carrito = get_or_create_carrito(request.user)

    if carrito.esta_vacio():
        messages.error(request, 'El carrito está vacío.')
        return redirect('carrito:ver_carrito')

    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente asociado.')
        return redirect('carrito:ver_carrito')

    items = carrito.items.select_related('producto').all()

    for item in items:
        disponible, stock_actual = verificar_stock(item.producto, item.talla, item.cantidad)
        if not disponible:
            messages.error(
                request,
                f'Stock insuficiente para {item.producto.nombre} talla {item.talla}. '
                f'Disponible: {stock_actual}.'
            )
            return redirect('carrito:ver_carrito')

    pedido = Pedido.objects.create(
        cliente=cliente,
        usuario=request.user,
        estado='pendiente',
        metodo_pago=request.POST.get('metodo_pago', 'efectivo'),
        total=carrito.get_total(),
        observaciones=request.POST.get('observaciones', ''),
    )

    for item in items:
        DetallePedido.objects.create(
            pedido=pedido,
            producto=item.producto,
            talla=item.talla,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            subtotal=item.get_subtotal(),
        )

        inv = Inventario.objects.get(producto=item.producto, talla=item.talla)
        inv.cantidad -= item.cantidad
        inv.save()

        if inv.cantidad == 0:
            notif_producto_agotado(item.producto)
        elif inv.cantidad <= 5:
            notif_stock_bajo(item.producto, inv.cantidad)

        MovimientoInventario.objects.create(
            producto=item.producto,
            talla=item.talla,
            tipo='salida',
            cantidad=item.cantidad,
            usuario=request.user,
            observacion=f'Venta Pedido #{pedido.id}',
        )

    carrito.vaciar()
    notif_nuevo_pedido(pedido)

    messages.success(request, f'Pedido #{pedido.id} creado exitosamente.')
    return redirect('pedidos:mi_pedido_detalle', pedido_id=pedido.id)