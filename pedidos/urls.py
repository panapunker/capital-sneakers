from django.urls import path
from . import views

urlpatterns = [

    path(
        'resumen/',
        views.resumen_pedidos,
        name='resumen_pedidos'
    ),

    path(
        'detalle/<int:pedido_id>/',
        views.detalle_pedido,
        name='detalle_pedido'
    ),
    path(
    'reportes/',
    views.reportes,
    name='reportes'
),

]