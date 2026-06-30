from django.contrib import admin
from .models import Pedido, DetallePedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estado', 'metodo_pago', 'total', 'fecha')
    list_filter = ('estado', 'metodo_pago', 'fecha')
    search_fields = ('cliente__nombre_completo', 'cliente__documento')
    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'talla', 'cantidad', 'precio_unitario', 'subtotal')