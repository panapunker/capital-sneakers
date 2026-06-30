"""
Funciones de métricas reutilizables del módulo Devoluciones.
Preparadas para: Dashboard, Reportes, Notificaciones.
No modifica dashboard/metrics.py existente; estas funciones
pueden importarse desde ahí cuando se decida integrarlas.
Todas las consultas usan aggregate/annotate/select_related.
"""
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta


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


def get_resumen_devoluciones():
    """
    Conteo general de devoluciones por estado.
    Reutilizable por: Dashboard, Notificaciones.
    """
    from .models import Devolucion
    datos = (
        Devolucion.objects
        .values('estado')
        .annotate(cantidad=Count('id'))
    )
    resumen = {d['estado']: d['cantidad'] for d in datos}
    return {
        'total': sum(resumen.values()),
        'pendientes': resumen.get('pendiente', 0),
        'aprobadas': resumen.get('aprobada', 0),
        'rechazadas': resumen.get('rechazada', 0),
        'finalizadas': resumen.get('finalizada', 0),
    }


def get_devoluciones_del_mes():
    """Cantidad de devoluciones creadas en el mes actual."""
    from .models import Devolucion
    inicio, fin = get_rango_mes()
    return Devolucion.objects.filter(
        fecha__date__gte=inicio,
        fecha__date__lte=fin,
    ).count()


def get_devoluciones_periodo(fecha_inicio, fecha_fin):
    """
    Métricas de devoluciones para un rango de fechas.
    Reutilizable por: Reportes, Dashboard.
    """
    from .models import Devolucion, DetalleDevolucion

    devoluciones = Devolucion.objects.filter(
        fecha__date__gte=fecha_inicio,
        fecha__date__lte=fecha_fin,
    )

    detalles = DetalleDevolucion.objects.filter(
        devolucion__fecha__date__gte=fecha_inicio,
        devolucion__fecha__date__lte=fecha_fin,
    ).select_related('devolucion', 'detalle_pedido')

    total_unidades = detalles.aggregate(total=Sum('cantidad'))['total'] or 0

    valor_devuelto = 0
    for d in detalles:
        valor_devuelto += d.detalle_pedido.precio_unitario * d.cantidad

    return {
        'total_devoluciones': devoluciones.count(),
        'total_unidades_devueltas': total_unidades,
        'valor_devuelto': valor_devuelto,
        'clientes_distintos': devoluciones.values('cliente').distinct().count(),
    }


def get_productos_mas_devueltos(limite=5):
    """
    Productos con más unidades devueltas.
    Reutilizable por: Dashboard, Reportes.
    """
    from .models import DetalleDevolucion
    return list(
        DetalleDevolucion.objects
        .values('producto__nombre', 'producto__referencia')
        .annotate(unidades=Sum('cantidad'))
        .order_by('-unidades')[:limite]
    )


def get_motivos_frecuentes(limite=5):
    """
    Motivos de devolución más comunes por tipo.
    Reutilizable por: Reportes.
    """
    from .models import Devolucion
    return list(
        Devolucion.objects
        .values('tipo')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')[:limite]
    )


def get_devoluciones_recientes(limite=5):
    """
    Últimas devoluciones registradas.
    Reutilizable por: Dashboard, Notificaciones.
    """
    from .models import Devolucion
    return (
        Devolucion.objects
        .select_related('pedido', 'cliente', 'usuario')
        .order_by('-fecha')[:limite]
    )