from .models import Notificacion


def notif_nuevo_pedido(pedido):
    cliente_nombre = ''
    if hasattr(pedido, 'cliente') and pedido.cliente:
        cliente_nombre = pedido.cliente.nombre_completo
    Notificacion.crear(
        tipo        = Notificacion.TIPO_NUEVO_PEDIDO,
        titulo      = f'Nuevo pedido #{pedido.pk}',
        descripcion = f'Cliente: {cliente_nombre}' if cliente_nombre else '',
        pedido_id   = pedido.pk,
    )


def notif_stock_bajo(producto, cantidad):
    Notificacion.crear(
        tipo        = Notificacion.TIPO_STOCK_BAJO,
        titulo      = f'Stock bajo: {producto.nombre}',
        descripcion = f'Quedan {cantidad} unidades en inventario.',
    )


def notif_producto_agotado(producto):
    Notificacion.crear(
        tipo        = Notificacion.TIPO_PRODUCTO_AGOTADO,
        titulo      = f'Producto agotado: {producto.nombre}',
        descripcion = 'El producto llegó a 0 unidades.',
    )


def notif_compra_recibida(compra):
    Notificacion.crear(
        tipo        = Notificacion.TIPO_COMPRA_RECIBIDA,
        titulo      = f'Compra #{compra.pk} recibida',
        descripcion = f'Proveedor: {compra.proveedor}',
        compra_id   = compra.pk,
    )


def notif_compra_cancelada(compra):
    Notificacion.crear(
        tipo        = Notificacion.TIPO_COMPRA_CANCELADA,
        titulo      = f'Compra #{compra.pk} cancelada',
        descripcion = f'Proveedor: {compra.proveedor}',
        compra_id   = compra.pk,
    )


def notif_nuevo_cliente(cliente):
    Notificacion.crear(
        tipo        = Notificacion.TIPO_NUEVO_CLIENTE,
        titulo      = f'Nuevo cliente: {cliente.nombre_completo}',
        descripcion = f'Documento: {cliente.documento}',
    )


def notif_sistema(titulo, descripcion=''):
    Notificacion.crear(
        tipo        = Notificacion.TIPO_SISTEMA,
        titulo      = titulo,
        descripcion = descripcion,
    )