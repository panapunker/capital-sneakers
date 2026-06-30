from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('',                    views.historial,          name='historial'),
    path('marcar/<int:pk>/',    views.marcar_leida,       name='marcar_leida'),
    path('marcar-todas/',       views.marcar_todas_leidas,name='marcar_todas_leidas'),
    path('recientes/',          views.obtener_recientes,  name='recientes'),
]