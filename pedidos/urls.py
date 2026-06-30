from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # Admin
    path('', views.pedido_lista, name='pedido_lista'),
    path('crear/', views.pedido_crear, name='pedido_crear'),
    path('<int:pedido_id>/', views.pedido_detalle, name='pedido_detalle'),
    path('<int:pedido_id>/estado/', views.pedido_estado, name='pedido_estado'),
    path('<int:pedido_id>/agregar/', views.pedido_agregar_detalle, name='pedido_agregar_detalle'),
    path('<int:pedido_id>/facturar/', views.facturar_pedido, name='facturar_pedido'),
    path('<int:pedido_id>/devolver/', views.devolver_pedido, name='devolver_pedido'),
    path('detalle/<int:detalle_id>/eliminar/', views.pedido_eliminar_detalle, name='pedido_eliminar_detalle'),
    path('<int:pedido_id>/factura-pdf/', views.factura_pdf, name='factura_pdf'),

    # Cliente
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<int:pedido_id>/', views.mi_pedido_detalle, name='mi_pedido_detalle'),
]