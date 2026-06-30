from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.cliente_lista, name='cliente_lista'),
    path('crear/', views.cliente_crear, name='cliente_crear'),
    path('<int:cliente_id>/', views.cliente_detalle, name='cliente_detalle'),
    path('<int:cliente_id>/editar/', views.cliente_editar, name='cliente_editar'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
]