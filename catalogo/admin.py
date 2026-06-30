from django.contrib import admin
from .models import Categoria, Marca, Producto, StockTalla


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


class StockTallaInline(admin.TabularInline):
    model = StockTalla
    extra = 0


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'referencia', 'marca', 'categoria', 'genero', 'precio_venta', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'genero', 'marca', 'categoria']
    search_fields = ['nombre', 'referencia']
    inlines = [StockTallaInline]