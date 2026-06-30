from django.contrib import admin
from .models import Proveedor, Compra, DetalleCompra


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'nit', 'contacto', 'telefono', 'estado']
    list_filter = ['estado']
    search_fields = ['empresa', 'nit']


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'proveedor', 'estado', 'fecha', 'usuario_creo']
    list_filter = ['estado', 'proveedor']
    inlines = [DetalleCompraInline]