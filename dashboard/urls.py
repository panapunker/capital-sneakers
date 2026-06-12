from django.urls import path
from . import views

urlpatterns = [

    path(
        'reportes/',
        views.reportes_admin,
        name='reportes_admin'
    ),

    path(
        'cliente/<int:user_id>/',
        views.detalle_cliente,
        name='detalle_cliente'
    ),

]