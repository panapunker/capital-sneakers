"""
Funciones reutilizables preparadas para el lector USB de código de barras.
El lector funciona como teclado: escribe el código y presiona Enter.
Estas funciones permiten, en el futuro, conectar un <input> que escuche
el evento 'Enter' y llame a estos buscadores sin reescribir lógica.

No implementa todavía la captura en tiempo real (JS/WebSockets).
Solo deja preparada la lógica de búsqueda backend.
"""
from inventario.models import Inventario


def buscar_inventario_por_codigo(codigo):
    """
    Busca un registro de Inventario (producto + talla) por su código de barras.
    Reutilizable por: Devoluciones, Pedidos, Compras, Inventario.
    """
    if not codigo:
        return None
    try:
        return Inventario.objects.select_related(
            'producto', 'producto__marca', 'producto__categoria'
        ).get(codigo_barras=codigo)
    except Inventario.DoesNotExist:
        return None


def buscar_pedido_por_codigo(codigo):
    """
    Preparado para buscar un pedido por código (ej: código impreso en factura).
    Actualmente busca por ID si el código es numérico.
    Reutilizable por: Devoluciones, Notificaciones.
    """
    from pedidos.models import Pedido
    if not codigo or not str(codigo).isdigit():
        return None
    return Pedido.objects.select_related('cliente').filter(id=int(codigo)).first()


def buscar_devolucion_por_codigo(codigo):
    """
    Preparado para buscar una devolución por código/ID.
    Reutilizable por: Dashboard, Reportes.
    """
    from .models import Devolucion
    if not codigo or not str(codigo).isdigit():
        return None
    return Devolucion.objects.select_related('pedido', 'cliente').filter(id=int(codigo)).first()


def buscar_producto_en_detalle_pedido(pedido, codigo):
    """
    Dado un pedido y un código de barras escaneado, identifica
    cuál DetallePedido corresponde (producto + talla) para
    preseleccionarlo automáticamente en el formulario de devolución.
    Reutilizable por: Devoluciones (creación masiva por escaneo).
    """
    inventario = buscar_inventario_por_codigo(codigo)
    if not inventario:
        return None

    return pedido.detalles.filter(
        producto=inventario.producto,
        talla=inventario.talla,
        devuelto=False,
    ).first()