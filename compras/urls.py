from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    # Proveedores
    path('proveedores/', views.proveedor_lista, name='proveedor_lista'),
    path('proveedores/nuevo/', views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/<int:pk>/editar/', views.proveedor_editar, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_eliminar, name='proveedor_eliminar'),

    # Compras
    path('', views.compra_lista, name='compra_lista'),
    path('nueva/', views.compra_crear, name='compra_crear'),
    path('<int:pk>/', views.compra_detalle, name='compra_detalle'),
    path('<int:pk>/agregar-detalle/', views.compra_agregar_detalle, name='compra_agregar_detalle'),
    path('detalle/<int:detalle_id>/eliminar/', views.compra_eliminar_detalle, name='compra_eliminar_detalle'),
    path('<int:pk>/confirmar-recepcion/', views.compra_confirmar_recepcion, name='compra_confirmar_recepcion'),
    path('<int:pk>/cancelar/', views.compra_cancelar, name='compra_cancelar'),

    # Reportes
    path('reportes/', views.reporte_compras, name='reporte_compras'),
]