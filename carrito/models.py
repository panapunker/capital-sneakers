from django.db import models
from django.conf import settings
from catalogo.models import Producto
from inventario.models import TALLAS_CHOICES


class Carrito(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    def __str__(self):
        return f"Carrito de {self.usuario.get_full_name() or self.usuario.username}"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_items(self):
        return sum(item.cantidad for item in self.items.all())

    def get_cantidad_productos(self):
        return self.items.count()

    def esta_vacio(self):
        return not self.items.exists()

    def vaciar(self):
        self.items.all().delete()


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='items_carrito'
    )
    talla = models.CharField(max_length=5, choices=TALLAS_CHOICES)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'
        unique_together = ('carrito', 'producto', 'talla')
        ordering = ['fecha_agregado']

    def __str__(self):
        return f"{self.producto.nombre} T{self.talla} x{self.cantidad}"

    def get_subtotal(self):
        return self.precio_unitario * self.cantidad

    def get_stock_disponible(self):
        from inventario.models import Inventario
        try:
            inv = Inventario.objects.get(producto=self.producto, talla=self.talla)
            return inv.cantidad
        except Inventario.DoesNotExist:
            return 0