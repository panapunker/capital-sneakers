from django.contrib import admin
from .models import Inventario, MovimientoInventario


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'talla', 'cantidad', 'fecha_actualizacion')
    list_filter = ('talla', 'producto__marca')
    search_fields = ('producto__nombre', 'producto__referencia')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'talla', 'tipo', 'cantidad', 'usuario', 'fecha')
    list_filter = ('tipo', 'fecha', 'usuario')
    search_fields = ('producto__nombre',)