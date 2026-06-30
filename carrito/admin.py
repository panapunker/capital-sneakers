from django.contrib import admin
from .models import Carrito, ItemCarrito


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ('precio_unitario', 'fecha_agregado', 'fecha_actualizacion')


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'get_total_items', 'get_total', 'fecha_actualizacion')
    inlines = [ItemCarritoInline]
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')