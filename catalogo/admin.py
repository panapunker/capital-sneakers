from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    list_display = (
        'nombre',
        'marca',
        'precio_compra',
        'precio',
        'ganancia_admin',
        'porcentaje_admin'
    )

    search_fields = (
        'nombre',
        'referencia'
    )

    list_filter = (
        'marca',
        'activo'
    )

    def ganancia_admin(self, obj):
        return obj.ganancia

    ganancia_admin.short_description = "Ganancia $"

    def porcentaje_admin(self, obj):
        return obj.porcentaje_ganancia

    porcentaje_admin.short_description = "% Ganancia"
