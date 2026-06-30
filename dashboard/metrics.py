"""
Funciones de métricas reutilizables.
Preparadas para: Dashboard, Reportes, Notificaciones, Contabilidad.
Todas las consultas están optimizadas con aggregate/annotate/select_related.
"""
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from datetime import timedelta


# ── Helpers de fechas ────────────────────────────────────────────────────────

def get_rango_hoy():
    hoy = timezone.now().date()
    return hoy, hoy

def get_rango_semana():
    hoy = timezone.now().date()
    inicio = hoy - timedelta(days=hoy.weekday())
    return inicio, hoy

def get_rango_mes():
    hoy = timezone.now().date()
    return hoy.replace(day=1), hoy

def get_rango_anio():
    hoy = timezone.now().date()
    return hoy.replace(month=1, day=1), hoy


# ── Métricas de Ventas ───────────────────────────────────────────────────────

def get_ventas_periodo(fecha_inicio, fecha_fin):
    """
    Retorna métricas de ventas para un rango de fechas.
    Reutilizable por: Dashboard, Reportes, Notificaciones.
    """
    from pedidos.models import Pedido, DetallePedido

    pedidos = Pedido.objects.filter(
        fecha__date__gte=fecha_inicio,
        fecha__date__lte=fecha_fin,
    ).exclude(estado='cancelado')

    resultado = pedidos.aggregate(
        total_ventas=Sum('total'),
        total_pedidos=Count('id'),
    )

    detalles = DetallePedido.objects.filter(
        pedido__fecha__date__gte=fecha_inicio,
        pedido__fecha__date__lte=fecha_fin,
    ).exclude(pedido__estado='cancelado')

    costo = detalles.aggregate(
        costo_total=Sum(
            ExpressionWrapper(
                F('cantidad') * F('producto__precio_compra'),
                output_field=DecimalField()
            )
        ),
        unidades_vendidas=Sum('cantidad'),
    )

    total_ventas = resultado['total_ventas'] or 0
    costo_total = costo['costo_total'] or 0

    return {
        'total_ventas': total_ventas,
        'total_pedidos': resultado['total_pedidos'] or 0,
        'unidades_vendidas': costo['unidades_vendidas'] or 0,
        'costo_total': costo_total,
        'utilidad': total_ventas - costo_total,
    }


def get_ventas_hoy():
    return get_ventas_periodo(*get_rango_hoy())

def get_ventas_mes():
    return get_ventas_periodo(*get_rango_mes())

def get_ventas_anio():
    return get_ventas_periodo(*get_rango_anio())


def get_ventas_por_mes(anios=1):
    """
    Ventas agrupadas por mes para Chart.js.
    Reutilizable por: Dashboard, Reportes, Gráficas.
    """
    from pedidos.models import Pedido
    desde = timezone.now() - timedelta(days=365 * anios)
    datos = (
        Pedido.objects
        .filter(fecha__gte=desde)
        .exclude(estado='cancelado')
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(total=Sum('total'), cantidad=Count('id'))
        .order_by('mes')
    )
    return list(datos)


# ── Métricas de Pedidos ──────────────────────────────────────────────────────

def get_resumen_pedidos():
    """
    Conteo de pedidos por estado.
    Reutilizable por: Dashboard, Notificaciones.
    """
    from pedidos.models import Pedido
    datos = (
        Pedido.objects
        .values('estado')
        .annotate(cantidad=Count('id'))
    )
    resumen = {d['estado']: d['cantidad'] for d in datos}
    return {
        'pendientes': resumen.get('pendiente', 0),
        'confirmados': resumen.get('confirmado', 0),
        'enviados': resumen.get('enviado', 0),
        'entregados': resumen.get('entregado', 0),
        'cancelados': resumen.get('cancelado', 0),
        'devueltos': resumen.get('devuelto', 0),
    }
def get_pedidos_recientes(limite=5):
    """
    Últimos pedidos para mostrar en el dashboard.
    Reutilizable por: Dashboard, Notificaciones, Tiempo real.
    """
    from pedidos.models import Pedido
    return (
        Pedido.objects
        .select_related('cliente')
        .order_by('-fecha')[:limite]
    )


# ── Métricas de Inventario ───────────────────────────────────────────────────

def get_resumen_inventario():
    """
    Métricas del inventario actual.
    Reutilizable por: Dashboard, Reportes, Notificaciones.
    """
    from inventario.models import Inventario
    from catalogo.models import Producto

    STOCK_MINIMO = 3

    inventarios = Inventario.objects.select_related(
        'producto', 'producto__categoria'
    )

    resumen = inventarios.aggregate(
        valor_compra=Sum(
            ExpressionWrapper(
                F('cantidad') * F('producto__precio_compra'),
                output_field=DecimalField()
            )
        ),
        valor_venta=Sum(
            ExpressionWrapper(
                F('cantidad') * F('producto__precio_venta'),
                output_field=DecimalField()
            )
        ),
        total_unidades=Sum('cantidad'),
    )

    sin_stock = inventarios.filter(cantidad=0).count()
    stock_bajo = inventarios.filter(cantidad__gt=0, cantidad__lte=STOCK_MINIMO).count()
    total_productos = Producto.objects.filter(activo=True).count()

    valor_compra = resumen['valor_compra'] or 0
    valor_venta = resumen['valor_venta'] or 0

    return {
        'total_productos': total_productos,
        'total_unidades': resumen['total_unidades'] or 0,
        'sin_stock': sin_stock,
        'stock_bajo': stock_bajo,
        'valor_compra': valor_compra,
        'valor_venta': valor_venta,
        'utilidad_estimada': valor_venta - valor_compra,
    }


def get_inventario_por_categoria():
    """
    Inventario agrupado por categoría para Chart.js.
    """
    from inventario.models import Inventario
    datos = (
        Inventario.objects
        .values('producto__categoria__nombre')
        .annotate(total=Sum('cantidad'))
        .order_by('-total')
    )
    return list(datos)


def get_productos_sin_stock():
    """Productos activos con stock 0 en todas sus tallas."""
    from inventario.models import Inventario
    return list(
        Inventario.objects
        .filter(cantidad=0)
        .select_related('producto', 'producto__marca', 'producto__categoria')
        .order_by('producto__nombre')
    )


def get_productos_stock_bajo(limite=3):
    """Productos con stock mayor a 0 pero menor o igual al límite."""
    from inventario.models import Inventario
    return list(
        Inventario.objects
        .filter(cantidad__gt=0, cantidad__lte=limite)
        .select_related('producto', 'producto__marca', 'producto__categoria')
        .order_by('cantidad')
    )


# ── Métricas de Clientes ──────────────────────────────────────────────────────

def get_resumen_clientes():
    """
    Métricas generales de clientes.
    Reutilizable por: Dashboard, Reportes, Notificaciones.
    """
    from clientes.models import Cliente
    from django.utils import timezone
    from datetime import timedelta

    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    hace_30 = hoy - timedelta(days=30)

    total = Cliente.objects.count()
    activos = Cliente.objects.filter(estado='activo').count()
    nuevos_mes = Cliente.objects.filter(fecha_registro__date__gte=inicio_mes).count()
    nuevos_30 = Cliente.objects.filter(fecha_registro__date__gte=hace_30).count()

    return {
        'total': total,
        'activos': activos,
        'inactivos': total - activos,
        'nuevos_mes': nuevos_mes,
        'nuevos_30_dias': nuevos_30,
    }


def get_clientes_top(limite=5):
    """
    Top clientes por total de compras.
    Reutilizable por: Dashboard, Reportes.
    """
    from clientes.models import Cliente
    return list(
        Cliente.objects
        .annotate(
            total_compras=Sum('pedidos__total'),
            total_pedidos=Count('pedidos'),
        )
        .filter(total_compras__isnull=False)
        .order_by('-total_compras')[:limite]
    )


# ── Métricas de Productos ─────────────────────────────────────────────────────

def get_productos_mas_vendidos(limite=5):
    """
    Productos más vendidos por unidades.
    Reutilizable por: Dashboard, Reportes, Recomendaciones.
    """
    from pedidos.models import DetallePedido
    return list(
        DetallePedido.objects
        .exclude(pedido__estado='cancelado')
        .values('producto__nombre', 'producto__referencia')
        .annotate(unidades=Sum('cantidad'))
        .order_by('-unidades')[:limite]
    )


# ── Métricas de Cliente individual ───────────────────────────────────────────

def get_resumen_cliente(cliente):
    """
    Resumen para el dashboard del cliente.
    Reutilizable por: Dashboard Cliente, Perfil.
    """
    if not cliente:
        return {}

    from pedidos.models import Pedido

    pedidos = Pedido.objects.filter(cliente=cliente)
    agg = pedidos.aggregate(
        total_gastado=Sum('total'),
        total_pedidos=Count('id'),
    )

    return {
        'total_pedidos':  agg['total_pedidos']  or 0,
        'total_gastado':  agg['total_gastado']  or 0,
        'pedidos_activos': pedidos.exclude(
            estado__in=['entregado', 'cancelado', 'devuelto']
        ).count(),
        'ultimo_pedido': pedidos.order_by('-fecha').first(),
    }