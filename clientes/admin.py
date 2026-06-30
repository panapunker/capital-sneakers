from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'documento', 'telefono', 'ciudad', 'estado', 'fecha_registro')
    list_filter = ('estado', 'ciudad')
    search_fields = ('nombre_completo', 'documento', 'correo')