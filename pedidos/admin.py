from django.contrib import admin

from .models import Pedido
from .models import DetallePedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'cliente',
        'fecha',
        'estado',
        'total_pedido'
    )

    list_filter = (
        'estado',
        'fecha'
    )

    search_fields = (
        'cliente__username',
        'cliente__email'
    )

    inlines = [
        DetallePedidoInline
    ]

    def total_pedido(self, obj):

        total = 0

        for item in obj.detalles.all():

            total += (
                item.precio *
                item.cantidad
            )

        return total

    total_pedido.short_description = "Total"


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):

    list_display = (
        'pedido',
        'producto',
        'talla',
        'cantidad',
        'precio',
        'precio_compra',
        'ganancia'
    )

    search_fields = (
        'producto__nombre',
    )

    def ganancia(self, obj):

        return (
            (obj.precio - obj.precio_compra)
            * obj.cantidad
        )

    ganancia.short_description = "Ganancia"
