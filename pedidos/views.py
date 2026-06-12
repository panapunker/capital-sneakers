from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Pedido


@login_required
def resumen_pedidos(request):

    pedidos = Pedido.objects.filter(
        cliente=request.user
    ).order_by('-fecha')

    return render(
        request,
        'pedidos/resumen.html',
        {
            'pedidos': pedidos
        }
    )


@login_required
def detalle_pedido(request, pedido_id):

    pedido = get_object_or_404(
        Pedido,
        id=pedido_id,
        cliente=request.user
    )

    return render(
        request,
        'pedidos/detalle.html',
        {
            'pedido': pedido
        }
    )


@login_required
def reportes(request):

    pedidos = Pedido.objects.filter(
        cliente=request.user
    ).order_by('-fecha')

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

    return render(
        request,
        'pedidos/reportes.html',
        {
            'pedidos': pedidos
        }
    )
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_cliente(request):

    pedidos = Pedido.objects.filter(
        cliente=request.user
    ).order_by('-fecha')

    total_comprado = 0
    entregados = 0
    devueltos = 0

    for pedido in pedidos:

        total_pedido = 0

        for item in pedido.detalles.all():

            total_pedido += (
                item.precio *
                item.cantidad
            )

        total_comprado += total_pedido

        if pedido.estado == 'entregado':
            entregados += 1

        if pedido.estado == 'devuelto':
            devueltos += 1

    filtro = request.GET.get('estado')

    if filtro:
        pedidos = pedidos.filter(
            estado=filtro
        )

    return render(
        request,
        'pedidos/dashboard_cliente.html',
        {
            'pedidos': pedidos,
            'total_comprado': total_comprado,
            'entregados': entregados,
            'devueltos': devueltos
        }
    )
