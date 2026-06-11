from pedidos.models import Pedido

def balance_cliente(request):

    if not request.user.is_authenticated:
        return {}

    pedidos = Pedido.objects.filter(
        cliente=request.user
    ).exclude(
        estado='cancelado'
    ).exclude(
        estado='pagado'
    )

    total = 0

    for pedido in pedidos:

        for item in pedido.detalles.all():

            total += item.subtotal()

    return {
        'balance_hoy': total
    }