from django.urls import path
from . import views

app_name = 'devoluciones'

urlpatterns = [
    # Listado y detalle
    path('', views.lista_devoluciones, name='lista'),
    path('<int:pk>/', views.detalle_devolucion, name='detalle'),

    # Crear devolución desde un pedido
    path('pedido/<int:pedido_id>/crear/', views.crear_devolucion, name='crear'),

    # Acciones sobre estado
    path('<int:pk>/aprobar/', views.aprobar_devolucion, name='aprobar'),
    path('<int:pk>/rechazar/', views.rechazar_devolucion, name='rechazar'),
    path('<int:pk>/finalizar/', views.finalizar_devolucion, name='finalizar'),
    path('<int:pk>/imprimir/', views.imprimir_devolucion, name='imprimir'),

    # Preparado para lector de código de barras (no implementado aún)
    path('api/buscar-codigo/', views.api_buscar_codigo_barras, name='api_buscar_codigo'),
]