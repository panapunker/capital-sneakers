from django.db import models
from django.contrib.auth.models import User

from catalogo.models import Producto
from inventario.models import Talla


class CarritoItem(models.Model):

    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )

    talla = models.ForeignKey(
        Talla,
        on_delete=models.CASCADE
    )

    cantidad = models.IntegerField(
        default=1
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return (
            f"{self.cliente} - "
            f"{self.producto}"
        )
