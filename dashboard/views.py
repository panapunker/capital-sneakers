from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

from pedidos.models import Pedido


@staff_member_required
def reportes_admin(request):

    pedidos = Pedido.objects.all().order_by('-fecha')

    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')

    if fecha_inicio:
        pedidos = pedidos.filter(
            fecha__date__gte=fecha_inicio
        )

    if fecha_fin:
        pedidos = pedidos.filter(
            fecha__date__lte=fecha_fin
        )

    ventas = 0
    inversion = 0

    clientes = {}

    for pedido in pedidos:

        total_pedido = 0

        for item in pedido.detalles.all():

            subtotal = item.precio * item.cantidad

            total_pedido += subtotal

            ventas += subtotal

            inversion += (
                item.precio_compra *
                item.cantidad
            )

        cliente = pedido.cliente.username

        if cliente not in clientes:

            clientes[cliente] = {
                'id': pedido.cliente.id,
                'pedidos': 0,
                'total': 0
            }

        clientes[cliente]['pedidos'] += 1
        clientes[cliente]['total'] += total_pedido

    ganancia = ventas - inversion

    return render(
        request,
        'dashboard/reportes_admin.html',
        {
            'pedidos': pedidos,
            'ventas': ventas,
            'inversion': inversion,
            'ganancia': ganancia,
            'clientes': clientes
        }
    )


@staff_member_required
def detalle_cliente(request, user_id):

    cliente = User.objects.get(
        id=user_id
    )

    pedidos = Pedido.objects.filter(
        cliente=cliente
    ).order_by('-fecha')

    total_compras = 0

    for pedido in pedidos:

        for item in pedido.detalles.all():

            total_compras += (
                item.precio *
                item.cantidad
            )

    return render(
        request,
        'dashboard/detalle_cliente.html',
        {
            'cliente': cliente,
            'pedidos': pedidos,
            'total_compras': total_compras
        }
    )