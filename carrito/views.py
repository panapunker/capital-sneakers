from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import CarritoItem
from catalogo.models import Producto
from inventario.models import Inventario
from pedidos.models import Pedido, DetallePedido


@login_required
def agregar_carrito(request, producto_id):

    if request.method == 'POST':

        inventario_id = request.POST.get('talla')
        cantidad = int(request.POST.get('cantidad', 1))

        inventario = Inventario.objects.get(
            id=inventario_id
        )

        if cantidad > inventario.cantidad:

            messages.error(
                request,
                'No hay suficiente inventario.'
            )

            return redirect(
                'detalle_producto',
                producto_id=producto_id
            )

        CarritoItem.objects.create(
            cliente=request.user,
            producto=inventario.producto,
            talla=inventario.talla,
            cantidad=cantidad
        )

        messages.success(
            request,
            'Producto agregado al carrito.'
        )

    return redirect('/catalogo/')
from django.shortcuts import render
from .models import CarritoItem


@login_required
def mi_pedido(request):

    items = CarritoItem.objects.filter(
        cliente=request.user
    )

    total = 0

    for item in items:
        total += item.subtotal()

    return render(
        request,
        'carrito/mi_pedido.html',
        {
            'items': items,
            'total': total
        }
    )
@login_required
def confirmar_pedido(request):

    items = CarritoItem.objects.filter(
        cliente=request.user
    )

    if not items.exists():

        messages.error(
            request,
            'No hay productos en el carrito.'
        )

        return redirect('mi_pedido')

    pedido = Pedido.objects.create(
        cliente=request.user
    )

    for item in items:

        DetallePedido.objects.create(
    pedido=pedido,
    producto=item.producto,
    talla=item.talla,
    cantidad=item.cantidad,
    precio=item.producto.precio,
    precio_compra=item.producto.precio_compra
)

        inventario = Inventario.objects.get(
            producto=item.producto,
            talla=item.talla
        )

        inventario.cantidad -= item.cantidad

        if inventario.cantidad < 0:
            inventario.cantidad = 0

        inventario.save()

    items.delete()

    messages.success(
        request,
        f'Pedido #{pedido.id} realizado exitosamente.'
    )

    return redirect('/catalogo/')
