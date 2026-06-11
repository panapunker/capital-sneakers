from django.urls import path
from . import views

urlpatterns = [

    path(
        'agregar/<int:producto_id>/',
        views.agregar_carrito,
        name='agregar_carrito'
    ),
    path(
    'mi-pedido/',
    views.mi_pedido,
    name='mi_pedido'
),
path(
    'confirmar/',
    views.confirmar_pedido,
    name='confirmar_pedido'
),

]