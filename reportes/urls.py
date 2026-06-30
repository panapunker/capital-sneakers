from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('ventas/',     views.reporte_ventas,     name='ventas'),
    path('inventario/', views.reporte_inventario,  name='inventario'),
    path('clientes/',   views.reporte_clientes,    name='clientes'),
    path('productos/',  views.reporte_productos,   name='productos'),
    path('exportar/<str:tipo>/', views.exportar_csv, name='exportar'),
    # ── Exportaciones Ventas ──
path("ventas/exportar/csv/",   views.exportar_ventas_csv,   name="exportar_ventas_csv"),
path("ventas/exportar/excel/", views.exportar_ventas_excel, name="exportar_ventas_excel"),
path("ventas/exportar/pdf/",   views.exportar_ventas_pdf,   name="exportar_ventas_pdf"),

# ── Exportaciones Inventario ──
path("inventario/exportar/csv/",   views.exportar_inventario_csv,   name="exportar_inventario_csv"),
path("inventario/exportar/excel/", views.exportar_inventario_excel, name="exportar_inventario_excel"),
path("inventario/exportar/pdf/",   views.exportar_inventario_pdf,   name="exportar_inventario_pdf"),

# ── Exportaciones Clientes ──
path("clientes/exportar/csv/",   views.exportar_clientes_csv,   name="exportar_clientes_csv"),
path("clientes/exportar/excel/", views.exportar_clientes_excel, name="exportar_clientes_excel"),
path("clientes/exportar/pdf/",   views.exportar_clientes_pdf,   name="exportar_clientes_pdf"),

# ── Exportaciones Productos ──
path("productos/exportar/csv/",   views.exportar_productos_csv,   name="exportar_productos_csv"),
path("productos/exportar/excel/", views.exportar_productos_excel, name="exportar_productos_excel"),
path("productos/exportar/pdf/",   views.exportar_productos_pdf,   name="exportar_productos_pdf"),
]