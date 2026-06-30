from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # Categorías
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nueva/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),

    # Marcas
    path('marcas/', views.lista_marcas, name='lista_marcas'),
    path('marcas/nueva/', views.crear_marca, name='crear_marca'),
    path('marcas/<int:pk>/editar/', views.editar_marca, name='editar_marca'),
    path('marcas/<int:pk>/eliminar/', views.eliminar_marca, name='eliminar_marca'),

    # Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('ver/',          views.catalogo_cliente,        name='catalogo_cliente'),
path('ver/<int:pk>/', views.producto_cliente_detalle, name='producto_cliente_detalle'),
]
