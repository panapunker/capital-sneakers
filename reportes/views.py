import csv
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, TruncDay, TruncYear

from pedidos.models import Pedido, DetallePedido
from inventario.models import Inventario, MovimientoInventario
from clientes.models import Cliente
from catalogo.models import Producto, Categoria
from . import exports


def es_admin(user):
    return user.is_staff or user.is_superuser


def get_rango_fechas(request):
    hoy = date.today()
    fecha_inicio = request.GET.get('fecha_inicio') or str(hoy.replace(day=1))
    fecha_fin    = request.GET.get('fecha_fin')    or str(hoy)
    return fecha_inicio, fecha_fin


# ─── VENTAS ──────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def reporte_ventas(request):
    fecha_inicio, fecha_fin = get_rango_fechas(request)
    estado  = request.GET.get('estado', '')
    agrupar = request.GET.get('agrupar', 'mes')

    pedidos = Pedido.objects.filter(
        fecha__date__gte=fecha_inicio,
        fecha__date__lte=fecha_fin,
    )
    if estado:
        pedidos = pedidos.filter(estado=estado)

    total_ingresos    = pedidos.exclude(estado='cancelado').aggregate(t=Sum('total'))['t'] or 0
    total_pedidos     = pedidos.count()
    pedidos_entregados = pedidos.filter(estado='entregado').count()
    pedidos_cancelados = pedidos.filter(estado='cancelado').count()
    ticket_promedio   = (total_ingresos / pedidos_entregados) if pedidos_entregados else 0
    tasa_cancelacion  = (pedidos_cancelados / total_pedidos * 100) if total_pedidos else 0

    metricas = {
        'total_ingresos':    total_ingresos,
        'total_pedidos':     total_pedidos,
        'pedidos_entregados': pedidos_entregados,
        'pedidos_cancelados': pedidos_cancelados,
        'ticket_promedio':   ticket_promedio,
        'tasa_cancelacion':  tasa_cancelacion,
    }

    if agrupar == 'dia':
        trunc = TruncDay('fecha')
        fmt   = '%d/%m'
    elif agrupar == 'anio':
        trunc = TruncYear('fecha')
        fmt   = '%Y'
    else:
        trunc = TruncMonth('fecha')
        fmt   = '%b %Y'

    ventas_periodo = (
        pedidos.exclude(estado='cancelado')
        .annotate(periodo_trunc=trunc)
        .values('periodo_trunc')
        .annotate(ingresos=Sum('total'), pedidos_count=Count('id'))
        .order_by('periodo_trunc')
    )

    grafica_ventas = {
        'labels':   [v['periodo_trunc'].strftime(fmt) for v in ventas_periodo if v['periodo_trunc']],
        'ingresos': [float(v['ingresos'] or 0)        for v in ventas_periodo],
        'pedidos':  [v['pedidos_count']               for v in ventas_periodo],
    }

    estados_data = (
        pedidos.values('estado')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    grafica_estados = {
        'labels': [e['estado'].capitalize() for e in estados_data],
        'datos':  [e['total']               for e in estados_data],
    }

    total_ing_global = float(total_ingresos) or 1
    top_raw = (
        DetallePedido.objects.filter(
            pedido__fecha__date__gte=fecha_inicio,
            pedido__fecha__date__lte=fecha_fin,
        )
        .exclude(pedido__estado='cancelado')
        .values('producto__nombre', 'producto__marca__nombre')
        .annotate(
            total_unidades=Sum('cantidad'),
            total_ingresos=Sum(F('cantidad') * F('precio_unitario')),
        )
        .order_by('-total_ingresos')[:10]
    )
    top_productos = []
    for item in top_raw:
        ing = float(item['total_ingresos'] or 0)
        top_productos.append({
            **item,
            'total_ingresos': ing,
            'porcentaje': (ing / total_ing_global * 100),
        })

    detalle_periodo = []
    for v in ventas_periodo:
        if not v['periodo_trunc']:
            continue
        ing = float(v['ingresos'] or 0)
        ped = v['pedidos_count']
        detalle_periodo.append({
            'periodo':     v['periodo_trunc'].strftime(fmt),
            'pedidos':     ped,
            'unidades':    0,   # calculado aparte si se necesita
            'ingresos':    ing,
            'ticket_prom': ing / ped if ped else 0,
        })

    context = {
        'filtros': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin':    fecha_fin,
            'estado':       estado,
            'agrupar':      agrupar,
        },
        'metricas':        metricas,
        'grafica_ventas':  grafica_ventas,
        'grafica_estados': grafica_estados,
        'top_productos':   top_productos,
        'detalle_periodo': detalle_periodo,
    }
    return render(request, 'reportes/ventas.html', context)


# ─── INVENTARIO ───────────────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def reporte_inventario(request):
    categoria_id    = request.GET.get('categoria', '')
    estado_stock    = request.GET.get('estado_stock', '')
    tipo_movimiento = request.GET.get('tipo_movimiento', '')

    inv_qs = Inventario.objects.select_related(
        'producto', 'producto__categoria', 'producto__marca'
    ).annotate(
        valor_total=ExpressionWrapper(
            F('cantidad') * F('producto__precio_venta'),
            output_field=DecimalField()
        )
    )

    if categoria_id:
        inv_qs = inv_qs.filter(producto__categoria__id=categoria_id)

    if estado_stock == 'critico':
        inv_qs = inv_qs.filter(cantidad=0)
    elif estado_stock == 'bajo':
        inv_qs = inv_qs.filter(cantidad__gte=1, cantidad__lte=5)
    elif estado_stock == 'normal':
        inv_qs = inv_qs.filter(cantidad__gte=6, cantidad__lte=20)
    elif estado_stock == 'alto':
        inv_qs = inv_qs.filter(cantidad__gt=20)

    inventario_list = inv_qs.order_by('cantidad')

    agg      = inv_qs.aggregate(total_unidades=Sum('cantidad'), valor_inventario=Sum('valor_total'))
    sin_stock = Inventario.objects.filter(cantidad=0).count()
    stock_bajo = Inventario.objects.filter(cantidad__gte=1, cantidad__lte=5).count()

    metricas = {
        'total_unidades':   agg['total_unidades']   or 0,
        'valor_inventario': agg['valor_inventario'] or 0,
        'sin_stock':        sin_stock,
        'stock_bajo':       stock_bajo,
    }

    alertas_criticas = (
        Inventario.objects.filter(cantidad__lte=2)
        .select_related('producto')
        .order_by('cantidad')
    )

    cat_data = (
        Inventario.objects.values('producto__categoria__nombre')
        .annotate(
            stock=Sum('cantidad'),
            valor=Sum(ExpressionWrapper(
                F('cantidad') * F('producto__precio_venta'),
                output_field=DecimalField()
            ))
        )
        .order_by('-stock')
    )
    grafica_categoria = {
        'labels': [c['producto__categoria__nombre'] or 'Sin categoría' for c in cat_data],
        'stock':  [c['stock'] or 0                                     for c in cat_data],
        'valor':  [float(c['valor'] or 0)                              for c in cat_data],
    }

    hace_6  = date.today() - timedelta(days=180)
    mov_qs  = MovimientoInventario.objects.filter(fecha__date__gte=hace_6)
    if tipo_movimiento:
        mov_qs = mov_qs.filter(tipo=tipo_movimiento)

    entradas = (mov_qs.filter(tipo='entrada')
                .annotate(mes=TruncMonth('fecha'))
                .values('mes').annotate(total=Sum('cantidad')).order_by('mes'))
    salidas  = (mov_qs.filter(tipo='salida')
                .annotate(mes=TruncMonth('fecha'))
                .values('mes').annotate(total=Sum('cantidad')).order_by('mes'))

    meses_labels = sorted(set(
        [e['mes'].strftime('%b %Y') for e in entradas if e['mes']] +
        [s['mes'].strftime('%b %Y') for s in salidas  if s['mes']]
    ))
    ent_dict = {e['mes'].strftime('%b %Y'): e['total'] for e in entradas if e['mes']}
    sal_dict = {s['mes'].strftime('%b %Y'): s['total'] for s in salidas  if s['mes']}

    grafica_movimientos = {
        'labels':   meses_labels,
        'entradas': [ent_dict.get(m, 0) for m in meses_labels],
        'salidas':  [sal_dict.get(m, 0) for m in meses_labels],
    }

    ultimos_movimientos = (
        MovimientoInventario.objects
        .select_related('producto', 'usuario')
        .order_by('-fecha')[:20]
    )

    context = {
        'filtros': {
            'categoria':       categoria_id,
            'estado_stock':    estado_stock,
            'tipo_movimiento': tipo_movimiento,
        },
        'categorias':           Categoria.objects.all(),
        'metricas':             metricas,
        'alertas_criticas':     alertas_criticas,
        'inventario':           inventario_list,
        'grafica_categoria':    grafica_categoria,
        'grafica_movimientos':  grafica_movimientos,
        'ultimos_movimientos':  ultimos_movimientos,
    }
    return render(request, 'reportes/inventario.html', context)


# ─── CLIENTES ────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def reporte_clientes(request):
    fecha_inicio, fecha_fin = get_rango_fechas(request)
    orden = request.GET.get('orden', '-total_compras')

    clientes_qs = (
          Cliente.objects
          .filter(
              pedidos__fecha__date__gte=fecha_inicio,
              pedidos__fecha__date__lte=fecha_fin,
              pedidos__facturado=True,
          )
          .annotate(
              total_pedidos=Count('pedidos', distinct=True),
              total_compras=Sum('pedidos__total'),
              promedio_compra=Avg('pedidos__total'),
          )
          .order_by(orden)
          .distinct()
      )

    total_clientes  = Cliente.objects.count()
    clientes_activos = clientes_qs.count()
    ingreso_total   = clientes_qs.aggregate(t=Sum('total_compras'))['t'] or 0
    ltv_promedio    = (float(ingreso_total) / clientes_activos) if clientes_activos else 0

    metricas = {
        'total_clientes':   total_clientes,
        'clientes_activos': clientes_activos,
        'ingreso_total':    ingreso_total,
        'ltv_promedio':     ltv_promedio,
    }

    nuevos = (
        Cliente.objects
        .annotate(mes=TruncMonth('fecha_registro'))
        .values('mes')
        .annotate(cantidad=Count('id'))
        .order_by('mes')
    )
    grafica_nuevos = {
        'labels': [n['mes'].strftime('%b %Y') for n in nuevos if n['mes']],
        'datos':  [n['cantidad']               for n in nuevos if n['mes']],
    }

    top10 = clientes_qs.order_by('-total_compras')[:10]
    grafica_top = {
        'labels': [c.nombre_completo for c in top10],
        'datos':  [float(c.total_compras or 0) for c in top10],
    }

    context = {
        'filtros': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin':    fecha_fin,
            'orden':        orden,
        },
        'metricas':      metricas,
        'clientes':      clientes_qs[:50],
        'grafica_nuevos': grafica_nuevos,
        'grafica_top':   grafica_top,
    }
    return render(request, 'reportes/clientes.html', context)


# ─── PRODUCTOS ───────────────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def reporte_productos(request):
    fecha_inicio, fecha_fin = get_rango_fechas(request)
    categoria_id = request.GET.get('categoria', '')
    orden        = request.GET.get('orden', '-total_vendido')

    productos_qs = (
        Producto.objects
        .filter(
            detalles_pedido__pedido__fecha__date__gte=fecha_inicio,
            detalles_pedido__pedido__fecha__date__lte=fecha_fin,
        )
        .annotate(
            total_vendido=Sum('detalles_pedido__cantidad'),
            total_ingresos=Sum(
                ExpressionWrapper(
                    F('detalles_pedido__cantidad') * F('detalles_pedido__precio_unitario'),
                    output_field=DecimalField()
                )
            ),
            stock_actual=Sum('inventarios__cantidad'),
        )
    )

    if categoria_id:
        productos_qs = productos_qs.filter(categoria__id=categoria_id)

    productos_qs = productos_qs.order_by(orden).distinct()

    total_productos   = Producto.objects.count()
    productos_activos = Producto.objects.filter(activo=True).count()
    total_vendidas    = productos_qs.aggregate(t=Sum('total_vendido'))['t'] or 0
    ingresos          = productos_qs.aggregate(t=Sum('total_ingresos'))['t'] or 0

    metricas = {
        'total_productos':   total_productos,
        'productos_activos': productos_activos,
        'total_vendidas':    total_vendidas,
        'ingresos_totales':  ingresos,
    }

    top10 = productos_qs.order_by('-total_vendido')[:10]
    grafica_unidades = {
        'labels': [p.nombre for p in top10],
        'datos':  [p.total_vendido or 0 for p in top10],
    }

    cat_ventas = (
        DetallePedido.objects
        .filter(
            pedido__fecha__date__gte=fecha_inicio,
            pedido__fecha__date__lte=fecha_fin,
        )
        .values('producto__categoria__nombre')
        .annotate(
            unidades=Sum('cantidad'),
            ingresos=Sum(F('cantidad') * F('precio_unitario')),
        )
        .order_by('-ingresos')
    )
    grafica_categoria = {
        'labels':   [c['producto__categoria__nombre'] or 'Sin categoría' for c in cat_ventas],
        'unidades': [c['unidades'] or 0                                   for c in cat_ventas],
        'ingresos': [float(c['ingresos'] or 0)                            for c in cat_ventas],
    }

    context = {
        'filtros': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin':    fecha_fin,
            'categoria':    categoria_id,
            'orden':        orden,
        },
        'categorias':        Categoria.objects.all(),
        'metricas':          metricas,
        'productos':         productos_qs[:50],
        'grafica_unidades':  grafica_unidades,
        'grafica_categoria': grafica_categoria,
    }
    return render(request, 'reportes/productos.html', context)


# ─── EXPORTAR CSV genérico (ruta existente) ──────────────────────────────────

@login_required
@user_passes_test(es_admin)
def exportar_csv(request, tipo):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo}.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)

    fecha_inicio = request.GET.get('fecha_inicio', str(date.today().replace(day=1)))
    fecha_fin    = request.GET.get('fecha_fin',    str(date.today()))

    if tipo == 'ventas':
        writer.writerow(['Pedido', 'Cliente', 'Fecha', 'Estado', 'Total'])
        qs = Pedido.objects.filter(
            fecha__date__gte=fecha_inicio,
            fecha__date__lte=fecha_fin,
        ).select_related('cliente')
        estado = request.GET.get('estado', '')
        if estado:
            qs = qs.filter(estado=estado)
        for p in qs:
            writer.writerow([p.id, p.cliente.nombre_completo,
                             p.fecha.strftime('%d/%m/%Y'), p.estado, p.total])

    elif tipo == 'inventario':
        writer.writerow(['Producto', 'Marca', 'Categoría', 'Talla', 'Cantidad', 'Precio Venta', 'Valor Total'])
        for inv in Inventario.objects.select_related('producto', 'producto__categoria', 'producto__marca'):
            writer.writerow([
                inv.producto.nombre,
                inv.producto.marca.nombre,
                inv.producto.categoria.nombre if inv.producto.categoria else '',
                inv.talla,
                inv.cantidad,
                inv.producto.precio_venta,
                float(inv.cantidad) * float(inv.producto.precio_venta),
            ])

    elif tipo == 'clientes':
        writer.writerow(['Cliente', 'Documento', 'Email', 'Teléfono', 'Ciudad', 'Estado'])
        for c in Cliente.objects.all():
            writer.writerow([c.nombre_completo, c.documento,
                             c.correo, c.telefono, c.ciudad, c.estado])

    elif tipo == 'productos':
        writer.writerow(['Producto', 'Referencia', 'Categoría', 'Precio Compra', 'Precio Venta', 'Activo'])
        for p in Producto.objects.select_related('categoria', 'marca'):
            writer.writerow([p.nombre, p.referencia,
                             p.categoria.nombre if p.categoria else '',
                             p.precio_compra, p.precio_venta, p.activo])

    return response


# ─── EXPORTACIONES INDIVIDUALES (rutas del paso 6) ───────────────────────────

@login_required
@user_passes_test(es_admin)
def exportar_ventas_csv(request):
    qs = Pedido.objects.select_related('cliente').all()
    return exports.csv_ventas(qs)

@login_required
@user_passes_test(es_admin)
def exportar_ventas_excel(request):
    qs = Pedido.objects.select_related('cliente').all()
    return exports.excel_ventas(qs)

@login_required
@user_passes_test(es_admin)
def exportar_ventas_pdf(request):
    qs = Pedido.objects.select_related('cliente').all()
    return exports.pdf_ventas(qs)

@login_required
@user_passes_test(es_admin)
def exportar_inventario_csv(request):
    qs = Inventario.objects.select_related('producto').all()
    return exports.csv_inventario(qs)

@login_required
@user_passes_test(es_admin)
def exportar_inventario_excel(request):
    qs = Inventario.objects.select_related('producto').all()
    return exports.excel_inventario(qs)

@login_required
@user_passes_test(es_admin)
def exportar_inventario_pdf(request):
    qs = Inventario.objects.select_related('producto').all()
    return exports.pdf_inventario(qs)

@login_required
@user_passes_test(es_admin)
def exportar_clientes_csv(request):
    qs = Cliente.objects.all()
    return exports.csv_clientes(qs)

@login_required
@user_passes_test(es_admin)
def exportar_clientes_excel(request):
    qs = Cliente.objects.all()
    return exports.excel_clientes(qs)

@login_required
@user_passes_test(es_admin)
def exportar_clientes_pdf(request):
    qs = Cliente.objects.all()
    return exports.pdf_clientes(qs)

@login_required
@user_passes_test(es_admin)
def exportar_productos_csv(request):
    qs = Producto.objects.select_related('categoria', 'marca').all()
    return exports.csv_productos(qs)

@login_required
@user_passes_test(es_admin)
def exportar_productos_excel(request):
    qs = Producto.objects.select_related('categoria', 'marca').all()
    return exports.excel_productos(qs)

@login_required
@user_passes_test(es_admin)
def exportar_productos_pdf(request):
    qs = Producto.objects.select_related('categoria', 'marca').all()
    return exports.pdf_productos(qs)
