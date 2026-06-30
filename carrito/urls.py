from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/', views.agregar_item, name='agregar_item'),
    path('eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('confirmar/', views.confirmar_carrito, name='confirmar_carrito'),
]