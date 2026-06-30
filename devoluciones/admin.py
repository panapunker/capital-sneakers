from django.contrib import admin
from .models import Devolucion, DetalleDevolucion, MovimientoDevolucion


class DetalleDevolucionInline(admin.TabularInline):
    model = DetalleDevolucion
    extra = 0
    readonly_fields = ('procesado',)


class MovimientoDevolucionInline(admin.TabularInline):
    model = MovimientoDevolucion
    extra = 0
    readonly_fields = ('accion', 'descripcion', 'usuario', 'fecha')
    can_delete = False


@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'cliente', 'tipo', 'estado', 'fecha')
    list_filter = ('estado', 'tipo')
    search_fields = ('pedido__id', 'cliente__nombre_completo', 'cliente__documento')
    inlines = [DetalleDevolucionInline, MovimientoDevolucionInline]
    readonly_fields = ('fecha', 'fecha_actualizacion')