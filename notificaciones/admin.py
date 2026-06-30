from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display  = ['tipo', 'titulo', 'usuario', 'leida', 'fecha']
    list_filter   = ['tipo', 'leida']
    search_fields = ['titulo', 'descripcion']