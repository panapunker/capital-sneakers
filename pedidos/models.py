from django.db import models
from django.contrib.auth.models import User

from catalogo.models import Producto
from inventario.models import Talla


class Pedido(models.Model):

    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )

    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente'
    )

    def __str__(self):
        return f"Pedido #{self.id}"


class DetallePedido(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )

    talla = models.ForeignKey(
        Talla,
        on_delete=models.CASCADE
    )

    cantidad = models.IntegerField()

    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    precio_compra = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    default=0
)

    def subtotal(self):
        return self.cantidad * self.precio

    def __str__(self):
        return (
            f"{self.producto} "
            f"- {self.talla}"
        )
