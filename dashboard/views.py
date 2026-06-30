from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .mixins import AdminRequiredMixin, ClienteRequiredMixin
from .metrics import (
    get_ventas_hoy, get_ventas_mes, get_ventas_anio,
    get_ventas_periodo, get_ventas_por_mes,
    get_resumen_pedidos, get_pedidos_recientes,
    get_resumen_inventario, get_inventario_por_categoria,
    get_productos_sin_stock, get_productos_stock_bajo,
    get_resumen_clientes, get_clientes_top,
    get_productos_mas_vendidos, get_resumen_cliente,
    get_rango_hoy, get_rango_semana, get_rango_mes, get_rango_anio,
)


# ── Dashboard Administrador ──────────────────────────────────────────────────

class AdminDashboardView(AdminRequiredMixin, View):
    template_name = 'dashboard/admin_dashboard.html'

    def get(self, request):
        ventas_hoy = get_ventas_hoy()
        ventas_mes = get_ventas_mes()
        ventas_anio = get_ventas_anio()
        pedidos = get_resumen_pedidos()
        inventario = get_resumen_inventario()
        clientes = get_resumen_clientes()

        # Gráficas
        ventas_mes_chart = get_ventas_por_mes()
        productos_top = get_productos_mas_vendidos(5)
        clientes_top = get_clientes_top(5)
        inventario_categorias = get_inventario_por_categoria()

        # Datos Chart.js
        chart_ventas_labels = [
            v['mes'].strftime('%b %Y') for v in ventas_mes_chart
        ]
        chart_ventas_data = [
            float(v['total']) for v in ventas_mes_chart
        ]
        chart_pedidos_labels = ['Pendientes', 'Confirmados', 'Enviados', 'Entregados', 'Cancelados', 'Devueltos']
        chart_pedidos_data = [
            pedidos['pendientes'], pedidos['confirmados'], pedidos['enviados'],
            pedidos['entregados'], pedidos['cancelados'], pedidos['devueltos'],
        ]
        chart_productos_labels = [p['producto__nombre'] for p in productos_top]
        chart_productos_data = [p['unidades'] for p in productos_top]
        chart_categorias_labels = [c['producto__categoria__nombre'] for c in inventario_categorias]
        chart_categorias_data = [c['total'] for c in inventario_categorias]

        from devoluciones.metrics import get_resumen_devoluciones, get_devoluciones_del_mes

        context = {
            # Ventas
            'ventas_hoy': ventas_hoy,
            'ventas_mes': ventas_mes,
            'ventas_anio': ventas_anio,
            # Devoluciones
            'devoluciones': get_resumen_devoluciones(),
            'devoluciones_mes': get_devoluciones_del_mes(),
            # Pedidos
            'pedidos': pedidos,
            'pedidos_recientes': get_pedidos_recientes(5),
            # Inventario
            'inventario': inventario,
            'productos_sin_stock': get_productos_sin_stock()[:5],
            'productos_stock_bajo': get_productos_stock_bajo()[:5],
            # Clientes
            'clientes': clientes,
            'clientes_top': clientes_top,
            # Chart.js
            'chart_ventas_labels': chart_ventas_labels,
            'chart_ventas_data': chart_ventas_data,
            'chart_pedidos_labels': chart_pedidos_labels,
            'chart_pedidos_data': chart_pedidos_data,
            'chart_productos_labels': chart_productos_labels,
            'chart_productos_data': chart_productos_data,
            'chart_categorias_labels': chart_categorias_labels,
            'chart_categorias_data': chart_categorias_data,
        }
        return render(request, self.template_name, context)


# ── Dashboard Cliente ────────────────────────────────────────────────────────

class ClienteDashboardView(ClienteRequiredMixin, View):
    template_name = 'dashboard/cliente_dashboard.html'

    def get(self, request):
        try:
            cliente = request.user.cliente
        except Exception:
            cliente = None

        resumen = get_resumen_cliente(cliente) if cliente else {}

        from pedidos.models import Pedido
        mis_pedidos = (
            Pedido.objects
            .filter(cliente=cliente)
            .order_by('-fecha')[:5]
        ) if cliente else []

        total_devoluciones = 0
        if cliente:
            from devoluciones.models import Devolucion
            total_devoluciones = Devolucion.objects.filter(cliente=cliente).count()

        context = {
            'cliente': cliente,
            'resumen': resumen,
            'mis_pedidos': mis_pedidos,
            'total_devoluciones': total_devoluciones,
            # Preparado para productos favoritos
            'productos_favoritos': [],
        }
        return render(request, self.template_name, context)


# ── Reportes ─────────────────────────────────────────────────────────────────

class ReportesView(AdminRequiredMixin, View):
    template_name = 'dashboard/reportes/index.html'

    def get(self, request):
        context = {
            'ventas_hoy': get_ventas_hoy(),
            'ventas_mes': get_ventas_mes(),
            'inventario': get_resumen_inventario(),
            'clientes': get_resumen_clientes(),
        }
        return render(request, self.template_name, context)


class ReporteVentasView(AdminRequiredMixin, View):
    template_name = 'dashboard/reportes/ventas.html'

    def get(self, request):
        filtro = request.GET.get('filtro', 'mes')
        fecha_inicio_str = request.GET.get('fecha_inicio')
        fecha_fin_str = request.GET.get('fecha_fin')

        if filtro == 'hoy':
            fecha_inicio, fecha_fin = get_rango_hoy()
        elif filtro == 'semana':
            fecha_inicio, fecha_fin = get_rango_semana()
        elif filtro == 'anio':
            fecha_inicio, fecha_fin = get_rango_anio()
        elif filtro == 'personalizado' and fecha_inicio_str and fecha_fin_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            except ValueError:
                fecha_inicio, fecha_fin = get_rango_mes()
        else:
            fecha_inicio, fecha_fin = get_rango_mes()

        ventas = get_ventas_periodo(fecha_inicio, fecha_fin)

        from pedidos.models import Pedido
        pedidos = (
            Pedido.objects
            .filter(fecha__date__gte=fecha_inicio, fecha__date__lte=fecha_fin)
            .select_related('cliente')
            .order_by('-fecha')
        )

        context = {
            'filtro': filtro,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'ventas': ventas,
            'pedidos': pedidos,
        }
        return render(request, self.template_name, context)


class ReporteInventarioView(AdminRequiredMixin, View):
    template_name = 'dashboard/reportes/inventario.html'

    def get(self, request):
        from inventario.models import Inventario
        from catalogo.models import Producto

        inventario = get_resumen_inventario()
        sin_stock = get_productos_sin_stock()
        stock_bajo = get_productos_stock_bajo()

        todos = (
            Inventario.objects
            .select_related('producto', 'producto__marca', 'producto__categoria')
            .order_by('producto__nombre', 'talla')
        )

        context = {
            'inventario': inventario,
            'sin_stock': sin_stock,
            'stock_bajo': stock_bajo,
            'todos': todos,
        }
        return render(request, self.template_name, context)


class ReporteClientesView(AdminRequiredMixin, View):
    template_name = 'dashboard/reportes/clientes.html'

    def get(self, request):
        from clientes.models import Cliente
        from django.db.models import Count
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)
        hace_90_dias = hoy - timedelta(days=90)

        clientes_top = get_clientes_top(10)
        nuevos = Cliente.objects.filter(
            fecha_registro__date__gte=inicio_mes
        ).order_by('-fecha_registro')

        inactivos = (
            Cliente.objects
            .filter(estado='activo')
            .exclude(pedidos__fecha__date__gte=hace_90_dias)
            .annotate(total_pedidos=Count('pedidos'))
            .order_by('nombre_completo')
        )

        context = {
            'resumen': get_resumen_clientes(),
            'clientes_top': clientes_top,
            'nuevos': nuevos,
            'inactivos': inactivos,
        }
        return render(request, self.template_name, context)


class ReporteProductosView(AdminRequiredMixin, View):
    template_name = 'dashboard/reportes/productos.html'

    def get(self, request):
        from pedidos.models import DetallePedido
        from catalogo.models import Producto
        from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField

        mas_vendidos = get_productos_mas_vendidos(10)

        menos_vendidos = (
            DetallePedido.objects
            .exclude(pedido__estado='cancelado')
            .values('producto__nombre', 'producto__referencia')
            .annotate(unidades=Sum('cantidad'))
            .order_by('unidades')[:10]
        )

        sin_ventas = (
            Producto.objects
            .filter(activo=True)
            .exclude(detalles_pedido__pedido__estado__in=['pendiente', 'confirmado', 'enviado', 'entregado'])
            .distinct()[:10]
        )

        mayor_utilidad = (
            DetallePedido.objects
            .exclude(pedido__estado='cancelado')
            .values('producto__nombre', 'producto__referencia')
            .annotate(
                ingresos=Sum('subtotal'),
                costo=Sum(
                    ExpressionWrapper(
                        F('cantidad') * F('producto__precio_compra'),
                        output_field=DecimalField()
                    )
                ),
            )
            .order_by('-ingresos')[:10]
        )

        context = {
            'mas_vendidos': mas_vendidos,
            'menos_vendidos': menos_vendidos,
            'sin_ventas': sin_ventas,
            'mayor_utilidad': mayor_utilidad,
        }
        return render(request, self.template_name, context)


# ── Exportaciones (estructura preparada) ────────────────────────────────────

def exportar_pdf(request):
    """Estructura preparada para exportación PDF con ReportLab."""
    return HttpResponse('Exportación PDF próximamente.', content_type='text/plain')


def exportar_excel(request):
    """Estructura preparada para exportación Excel con openpyxl."""
    return HttpResponse('Exportación Excel próximamente.', content_type='text/plain')


def exportar_csv(request):
    """Estructura preparada para exportación CSV."""
    return HttpResponse('Exportación CSV próximamente.', content_type='text/plain')


# ── API Métricas (preparado para notificaciones en tiempo real) ──────────────

def api_metricas(request):
    """
    Endpoint JSON con métricas principales.
    Preparado para: Notificaciones, WebSockets, actualización automática.
    """
    if not request.user.is_authenticated or not request.user.es_admin:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    data = {
        'ventas_hoy': get_ventas_hoy(),
        'pedidos': get_resumen_pedidos(),
        'inventario': {
            'sin_stock': get_resumen_inventario()['sin_stock'],
            'stock_bajo': get_resumen_inventario()['stock_bajo'],
        },
        'timestamp': timezone.now().isoformat(),
    }

    # Convertir Decimal a float para JSON
    def convert(obj):
        import decimal
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return obj

    import json
    return HttpResponse(
        json.dumps(data, default=convert),
        content_type='application/json'
    )