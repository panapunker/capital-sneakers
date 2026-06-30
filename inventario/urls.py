from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.inventario_lista, name='lista'),
    path('producto/<int:producto_id>/', views.inventario_detalle, name='detalle'),
    path('producto/<int:producto_id>/ajustar/', views.inventario_ajustar, name='ajustar'),
    path('movimientos/', views.movimientos_lista, name='movimientos'),
]