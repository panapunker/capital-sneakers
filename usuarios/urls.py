from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.usuario_lista, name='usuario_lista'),
    path('nuevo/', views.usuario_crear, name='usuario_crear'),
    path('<int:pk>/', views.usuario_detalle, name='usuario_detalle'),
    path('<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('<int:pk>/activar/', views.usuario_activar, name='usuario_activar'),
    path('<int:pk>/desactivar/', views.usuario_desactivar, name='usuario_desactivar'),
    path('<int:pk>/cambiar-password/', views.usuario_cambiar_password, name='usuario_cambiar_password'),
]