# reportes/exports.py
from django.http import HttpResponse
from django.utils import timezone


def _filename(nombre, ext):
    ts = timezone.now().strftime("%Y%m%d_%H%M%S")
    return f"capital_sneakers_{nombre}_{ts}.{ext}"


# ── CSV ──────────────────────────────────────────────────────────────────────

def _csv_response(nombre):
    r = HttpResponse(content_type='text/csv; charset=utf-8')
    r['Content-Disposition'] = f'attachment; filename="{_filename(nombre, "csv")}"'
    r.write('\ufeff')
    return r


def csv_ventas(queryset):
    import csv
    response = _csv_response('ventas')
    w = csv.writer(response)
    w.writerow(['ID', 'Cliente', 'Fecha', 'Estado', 'Método Pago', 'Total'])
    for p in queryset:
        w.writerow([
            p.id,
            p.cliente.nombre_completo,
            p.fecha.strftime('%d/%m/%Y %H:%M'),
            p.get_estado_display(),
            p.get_metodo_pago_display(),
            p.total,
        ])
    return response


def csv_inventario(queryset):
    import csv
    response = _csv_response('inventario')
    w = csv.writer(response)
    w.writerow(['Producto', 'Referencia', 'Marca', 'Talla', 'Cantidad', 'Precio Venta', 'Valor Total'])
    for inv in queryset:
        w.writerow([
            inv.producto.nombre,
            inv.producto.referencia,
            inv.producto.marca.nombre,
            inv.talla,
            inv.cantidad,
            inv.producto.precio_venta,
            float(inv.cantidad) * float(inv.producto.precio_venta),
        ])
    return response


def csv_clientes(queryset):
    import csv
    response = _csv_response('clientes')
    w = csv.writer(response)
    w.writerow(['Nombre', 'Documento', 'Correo', 'Teléfono', 'Ciudad', 'Estado', 'Fecha Registro'])
    for c in queryset:
        w.writerow([
            c.nombre_completo, c.documento, c.correo,
            c.telefono, c.ciudad, c.get_estado_display(),
            c.fecha_registro.strftime('%d/%m/%Y'),
        ])
    return response


def csv_productos(queryset):
    import csv
    response = _csv_response('productos')
    w = csv.writer(response)
    w.writerow(['Nombre', 'Referencia', 'Marca', 'Categoría', 'Precio Compra', 'Precio Venta', 'Activo'])
    for p in queryset:
        w.writerow([
            p.nombre, p.referencia,
            p.marca.nombre,
            p.categoria.nombre if p.categoria else '',
            p.precio_compra, p.precio_venta, p.activo,
        ])
    return response


# ── EXCEL ─────────────────────────────────────────────────────────────────────

def _excel_response(nombre):
    r = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    r['Content-Disposition'] = f'attachment; filename="{_filename(nombre, "xlsx")}"'
    return r


def excel_ventas(queryset):
    # TODO: implementar con openpyxl
    return _excel_response('ventas')

def excel_inventario(queryset):
    return _excel_response('inventario')

def excel_clientes(queryset):
    return _excel_response('clientes')

def excel_productos(queryset):
    return _excel_response('productos')


# ── PDF ───────────────────────────────────────────────────────────────────────

def _pdf_response(nombre):
    r = HttpResponse(content_type='application/pdf')
    r['Content-Disposition'] = f'attachment; filename="{_filename(nombre, "pdf")}"'
    return r


def pdf_ventas(queryset):
    # TODO: implementar con WeasyPrint
    return _pdf_response('ventas')

def pdf_inventario(queryset):
    return _pdf_response('inventario')

def pdf_clientes(queryset):
    return _pdf_response('clientes')

def pdf_productos(queryset):
    return _pdf_response('productos')