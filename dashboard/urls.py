from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard
    path('', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('cliente/', views.ClienteDashboardView.as_view(), name='cliente_dashboard'),

    # Reportes
    path('reportes/', views.ReportesView.as_view(), name='reportes'),
    path('reportes/ventas/', views.ReporteVentasView.as_view(), name='reporte_ventas'),
    path('reportes/inventario/', views.ReporteInventarioView.as_view(), name='reporte_inventario'),
    path('reportes/clientes/', views.ReporteClientesView.as_view(), name='reporte_clientes'),
    path('reportes/productos/', views.ReporteProductosView.as_view(), name='reporte_productos'),

    # Exportaciones (estructura preparada)
    path('reportes/exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('reportes/exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('reportes/exportar/csv/', views.exportar_csv, name='exportar_csv'),

    # API métricas (preparado para notificaciones y tiempo real)
    path('api/metricas/', views.api_metricas, name='api_metricas'),
]