from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from pedidos.models import Pedido


@staff_member_required
def reportes_admin(request):

    pedidos = Pedido.objects.filter(
        estado='pagado'
    ).order_by('-fecha')

    inversion = 0
    ventas = 0

    for pedido in pedidos:

        for item in pedido.detalles.all():

            ventas += (
                item.precio *
                item.cantidad
            )

            inversion += (
                item.producto.precio_compra *
                item.cantidad
            )

    ganancia = ventas - inversion

    return render(
        request,
        'dashboard/reportes_admin.html',
        {
            'pedidos': pedidos,
            'ventas': ventas,
            'inversion': inversion,
            'ganancia': ganancia
        }
    )