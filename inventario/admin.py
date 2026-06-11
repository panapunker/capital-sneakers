from django.contrib import admin

from .models import Talla
from .models import Inventario


@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):

    list_display = (
        'nombre',
    )


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):

    list_display = (
        'producto',
        'talla',
        'cantidad'
    )

    search_fields = (
        'producto__nombre',
        'producto__referencia'
    )

    list_filter = (
        'talla',
    )
