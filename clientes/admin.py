from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = (
        'nombre_negocio',
        'propietario',
        'telefono',
        'ciudad',
        'activo'
    )

    search_fields = (
        'nombre_negocio',
        'propietario',
        'telefono'
    )

    list_filter = (
        'activo',
        'ciudad'
    )
